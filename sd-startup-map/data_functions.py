from models import Tag, Company
import streamlit as st
from n4j import execute_query


@st.cache_data
def get_tags():
    print(f"get_tags called")
    tags_query = """
    MATCH (c:Company)-[:TAGGED]-(t)
    RETURN DISTINCT t
    ORDER BY t.Name
    """
    records, _, _ = execute_query(tags_query, {})
    results = []
    for r in records:
        # print(f"process tag record: {r}")
        data = r.data()["t"]
        try:
            tag = Tag(**data)
            results.append(tag)
        except Exception as e:
            print(f"\nProblem parsing Tag record: {r}: {e}")
            continue
    return results


def sorted_tags():
    tags_list = get_tags()
    return sorted(set(t.Name for t in tags_list))


@st.cache_data
def get_companies(tags: list[str]):

    print(f"\ntags for retrieving companies: {tags}")

    if len(tags) > 0:
        query = """
        MATCH (l:Location)<-[:HAS_OFFICE]-(c:Company)-[:TAGGED]->(t)
        WHERE t.Name IN $tags
        RETURN DISTINCT c.Id as Id, c.Description as Description, c.StartupYear as StartupYear, c.LinkedInUrl as LinkedInUrl, c.Url as Url, c.Name as Name, c.Logo as Logo, l.Latitude as Lat, l.Longitude as Lon, collect(t.Name) as Tags
        """
        params = {"tags": tags}
    else:
        query = """
        MATCH (l:Location)<-[:HAS_OFFICE]-(c:Company)-[:TAGGED]->(t)
        RETURN DISTINCT c.Id as Id, c.Description as Description, c.StartupYear as StartupYear, c.LinkedInUrl as LinkedInUrl, c.Url as Url, c.Name as Name, c.Logo as Logo, l.Latitude as Lat, l.Longitude as Lon, collect(t.Name) as Tags
        """
        params = {}

    records, _, _ = execute_query(query, params)

    # print(f"Company query response: {records}")

    results = []
    for r in records:
        data = r.data()
        # print(f"company record data: {data}")
        try:
            company = Company(**data)
            results.append(company)
        except Exception as e:
            print(f"\nProblem parsing Company record: {r}: {e}")
            continue

    return results


def find_company(name: str) -> Company:
    query = """
    MATCH (l:Location)<-[:HAS_OFFICE]-(c:Company)-[:TAGGED]->(t)
    WHERE c.Name = $name
    RETURN c.Id as Id, c.Description as Description, c.StartupYear as StartupYear, c.LinkedInUrl as LinkedInUrl, c.Url as Url, c.Name as Name, c.Logo as Logo, l.Latitude as Lat, l.Longitude as Lon, collect(t.Name) as Tags
    """
    params = {"name": name}
    records, _, _ = execute_query(query, params)
    for r in records:
        data = r.data()
        try:
            company = Company(**data)
            return company
        except Exception as e:
            print(f"\nProblem parsing Company record: {r}: {e}")
            continue
    return None


# def edit_company
