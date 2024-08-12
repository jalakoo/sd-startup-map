from models import Tag, Company
import streamlit as st
from n4j import execute_query
import uuid
import datetime
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import logging


@st.cache_data(ttl=15)
def get_tags():
    logging.debug(f"get_tags called")
    tags_query = """
    MATCH (c:Company)-[:TAGGED]-(t)
    RETURN DISTINCT t
    ORDER BY t.Name
    """
    records, _, _ = execute_query(tags_query, {})
    results = []
    for r in records:
        data = r.data()["t"]
        try:
            tag = Tag(**data)
            results.append(tag)
        except Exception as e:
            logging.error(f"\nProblem parsing Tag record: {r}: {e}")
            continue
    return results


def sorted_tags():
    tags_list = get_tags()
    return sorted(set(t.Name for t in tags_list))


@st.cache_data(ttl=15)
def get_companies(tags: list[str]):

    if len(tags) > 0:
        query = """
        MATCH (l:Location)<-[:HAS_OFFICE]-(c:Company)-[:TAGGED]->(t)
        WHERE t.Name IN $tags
        RETURN DISTINCT c.UUID as UUID, c.Description as Description, c.StartupYear as StartupYear, c.LinkedInUrl as LinkedInUrl, c.Url as Url, c.Name as Name, c.Logo as Logo, l.Latitude as Lat, l.Longitude as Lon, collect(t.Name) as Tags,l.Address as Address, l.City as City, l.State as State, l.Zip as Zip
        """
        params = {"tags": tags}
    else:
        query = """
        MATCH (l:Location)<-[:HAS_OFFICE]-(c:Company)-[:TAGGED]->(t)
        RETURN DISTINCT c.UUID as UUID, c.Description as Description, c.StartupYear as StartupYear, c.LinkedInUrl as LinkedInUrl, c.Url as Url, c.Name as Name, c.Logo as Logo, l.Latitude as Lat, l.Longitude as Lon, collect(t.Name) as Tags, l.Address as Address, l.City as City, l.State as State, l.Zip as Zip
        """
        params = {}

    records, _, _ = execute_query(query, params)

    results = []
    for r in records:
        data = r.data()
        try:
            company = Company(**data)
            results.append(company)
        except Exception as e:
            logging.debug(f"\nProblem parsing Company record: {r}: {e}. Skipping...")
            continue

    return results


def find_company(name: str) -> Company:
    query = """
    MATCH (l:Location)<-[:HAS_OFFICE]-(c:Company)-[:TAGGED]->(t)
    WHERE c.Name = $name
    RETURN c.UUID as UUID, c.Description as Description, c.StartupYear as StartupYear, c.LinkedInUrl as LinkedInUrl, c.Url as Url, c.Name as Name, c.Logo as Logo, l.Latitude as Lat, l.Longitude as Lon, collect(t.Name) as Tags,l.Address as Address, l.City as City, l.State as State, l.Zip as Zip
    """
    params = {"name": name}
    records, _, _ = execute_query(query, params)
    for r in records:
        data = r.data()
        try:
            company = Company(**data)
            return company
        except Exception as e:
            logging.debug(f"\nProblem parsing Company record: {r}: {e}. Skipping...")
            continue
    return None


# def edit_company


def create_new_tags(tags: list[str]):
    query = """
    UNWIND $tags as tag
    MERGE (t:Tag {
        Name: tag
    })
    """
    params = {"tags": tags}
    return execute_query(query, params)


@st.cache_data(ttl=10)
def get_lat_lon_from_address(street_address, city, state, zip_code):
    address = f"{street_address}, {city}, {state}, {zip_code}"

    try:
        loc = Nominatim(user_agent="Geopy Library")

        # entering the location name
        getLoc = loc.geocode(address)

        return getLoc.latitude, getLoc.longitude

    except (GeocoderTimedOut, GeocoderServiceError) as e:
        logging.error(f"Geocoding error: {e}")
        return None, None


def create_new_location(address: str, city: str, state: str, zip: str):

    # Find latitude and longitude from address
    lat, lon = get_lat_lon_from_address(address, city, state, zip)

    if lat is None or lon is None:
        logging.error(
            f"Error: Unable to find latitude and longitude for address: {address}"
        )
        raise ValueError("Unable to find latitude and longitude for address")

    query = """
    MERGE (l:Location {
        Address: $address,
        City: $city,
        State: $state,
        ZipCode: $zip
    })
    ON CREATE SET
        l.Latitude = $lat,
        l.Longitude = $lon
    """
    params = {
        "address": address,
        "city": city,
        "state": state,
        "zip": zip,
        "lat": lat,
        "lon": lon,
    }
    return execute_query(query, params)


def add_company(company: Company):

    # Create Location
    # print(f"\nCreating new location for company: {company.__dict__}")

    _, summary, _ = create_new_location(
        company.Address, company.City, company.State, company.ZipCode
    )
    logging.debug(
        f"Created new location for company: {company.Name} with summary: {summary.__dict__}"
    )

    # Create Company
    query = """
    MERGE (c:Company {Url: $Url})
    ON CREATE SET
        c.Id = $Id,
        c.UUID = $UUID,
        c.Description = $Description,
        c.StartupYear = $StartupYear,
        c.LinkedInUrl = $LinkedInUrl,
        c.Name = $Name,
        c.Logo = $Logo
    """
    params = {
        "Id": company.Id,
        "UUID": str(uuid.uuid4()),
        "Description": company.Description,
        "StartupYear": company.StartupYear,
        "LinkedInUrl": company.LinkedInUrl,
        "Url": company.Url,
        "Name": company.Name,
        "Logo": company.Logo,
        "Lat": company.Lat,
        "Lon": company.Lon,
    }
    _, summary, _ = execute_query(query, params)
    logging.debug(f"Company created: {summary.__dict__}")

    # Create Company -> Office relationship
    query = """_
    MATCH (l:Location {Latitude: $Lat, Longitude: $Lon}),(c:Company {Url: $Url})
    MERGE (c)-[:HAS_OFFICE]->(l)
    """
    params = {
        "Url": company.Url,
        "Lat": company.Lat,
        "Lon": company.Lon,
    }
    _, summary, _ = execute_query(query, params)
    logging.debug(
        f"(Company)-[:HAS_OFFICE]->(Location) relationship created: {summary.__dict__}"
    )

    # Create Tags
    _, summary, _ = create_new_tags(company.Tags)
    logging.debug(f"Tags created: {summary.__dict__}")

    # Create Company -> Tags Relationships
    query = """
    UNWIND $tags as tag
    MATCH (c:Company {Url: $Url}), (t:Tag {Name: tag})
    MERGE (c)-[:TAGGED]->(t)
    """
    params = {
        "Url": company.Url,
        "tags": company.Tags,
    }
    _, summary, _ = execute_query(query, params)
    logging.debug(
        f"(Company)-[:TAGGED]->(Tag) relationships created: {summary.__dict__}"
    )

    return


def update_company(original: Company, new: Company):

    # Create New Location if needed
    if (
        original.Address != new.Address
        or original.City != new.City
        or original.State != new.State
        or original.ZipCode != new.ZipCode
    ):
        _, summary, _ = create_new_location(
            new.Address, new.City, new.State, new.ZipCode
        )
        logging.debug(
            f"Created new location for updated company: '{new.Name}' with summary: {summary.__dict__}"
        )

        # Remove old (Company)-[:HAS_OFFICE]->(Location) relationship
        query = """
        MATCH (l:Location {Latitude: $Lat, Longitude: $Lon}),(c:Company {Url: $Url})
        MATCH (c)-[r:HAS_OFFICE]->(l)
        MERGE (c)-[:HAD_OFFICE]->(l)
        DELETE r
        """
        params = {
            "Url": new.Url,
            "Lat": new.Lat,
            "Lon": new.Lon,
        }
        _, summary, _ = execute_query(query, params)
        logging.debug(
            f"(Company)-[:HAS_OFFICE]->(Location) relationship converted to [:HAD_OFFICE]: {summary.__dict__}"
        )

        # Add new (Company)-[:HAS_OFFICE]->(Location) relationship
        query = """
        MATCH (l:Location {Latitude: $Lat, Longitude: $Lon}),(c:Company {Url: $Url})
        MERGE (c)-[:HAS_OFFICE]->(l)
        """
        params = {
            "Url": new.Url,
            "Lat": new.Lat,
            "Lon": new.Lon,
        }
        _, summary, _ = execute_query(query, params)
        logging.debug(
            f"(Company)-[:HAS_OFFICE]->(Location) relationship created: {summary.__dict__}"
        )

    # Update Company record
    query = """
    MATCH (c:Company {UUID: $UUID})
    SET
        c.Url = $Url,
        c.Description = $Description,
        c.StartupYear = $StartupYear,
        c.LinkedInUrl = $LinkedInUrl,
        c.Name = $Name,
        c.Logo = $Logo,
    """
    params = {
        "UUID": original.UUID,
        "Url": new.Url,
        "Description": new.Description,
        "StartupYear": new.StartupYear,
        "LinkedInUrl": new.LinkedInUrl,
        "Name": new.Name,
        "Logo": new.Logo,
    }

    # Remove old tags
    query = """
    MATCH (c:Company {UUID: $UUID})-[r:TAGGED]->(t:Tag)
    DELETE r
    """
    params = {
        "UUID": original.UUID,
    }
    _, summary, _ = execute_query(query, params)
    logging.debug(
        f"Old tags removed from company: '{original.Name}' with summary: {summary.__dict__}"
    )

    # Add any new tags
    _, summary, _ = create_new_tags(new.Tags)
    logging.debug(f"Tags created: {summary.__dict__}")

    # Add (Company)-[:TAGGED]->(Tag) relationships
    query = """
    UNWIND $tags as tag
    MATCH (c:Company {UUID: $UUID}), (t:Tag {Name: tag})
    MERGE (c)-[:TAGGED]->(t)
    """

    return


def delete_company(uuid: str):
    # Remove (Company)-[:TAGGED]->(Tag) relationships
    query = """
    MATCH (c:Company {UUID: $UUID})
    DETACH DELETE c
    """
    params = {
        "UUID": uuid,
    }
    _, summary, _ = execute_query(query, params)
    logging.debug(f"Company deleted: {summary.__dict__}")
