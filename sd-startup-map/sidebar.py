import streamlit as st
import auth_functions
from data_functions import find_company
from datetime import datetime
from data_functions import sorted_tags, add_company, delete_company, update_company
from models import Company
import logging


def sidebar():
    ## -------------------------------------------------------------------------------------------------
    ## Not logged in -----------------------------------------------------------------------------------
    ## -------------------------------------------------------------------------------------------------
    with st.sidebar:
        if "user_info" not in st.session_state:

            # Authentication form layout
            do_you_have_an_account = st.selectbox(
                label="Do you have an account?",
                options=("Yes", "I forgot my password"),
            )
            auth_form = st.form(key="Authentication form", clear_on_submit=False)
            email = auth_form.text_input(label="Email")
            password = (
                auth_form.text_input(label="Password", type="password")
                if do_you_have_an_account in {"Yes", "No"}
                else auth_form.empty()
            )
            auth_notification = st.empty()

            # Sign In
            if do_you_have_an_account == "Yes" and auth_form.form_submit_button(
                label="Sign In", use_container_width=True, type="primary"
            ):
                with auth_notification, st.spinner("Signing in"):
                    auth_functions.sign_in(email, password)

            # Create Account
            elif do_you_have_an_account == "No" and auth_form.form_submit_button(
                label="Create Account", use_container_width=True, type="primary"
            ):
                with auth_notification, st.spinner("Creating account"):
                    auth_functions.create_account(email, password)

            # Password Reset
            elif (
                do_you_have_an_account == "I forgot my password"
                and auth_form.form_submit_button(
                    label="Send Password Reset Email",
                    use_container_width=True,
                    type="primary",
                )
            ):
                with auth_notification, st.spinner("Sending password reset link"):
                    auth_functions.reset_password(email)

            # Authentication success and warning messages
            if "auth_success" in st.session_state:
                auth_notification.success(st.session_state.auth_success)
                del st.session_state.auth_success
            elif "auth_warning" in st.session_state:
                auth_notification.warning(st.session_state.auth_warning)
                del st.session_state.auth_warning

        ## -------------------------------------------------------------------------------------------------
        ## Logged in --------------------------------------------------------------------------------------
        ## -------------------------------------------------------------------------------------------------
        else:
            # Show user information
            # st.header("User information:")
            # st.write(st.session_state.user_info)
            st.header(f"Logged in as {st.session_state.user_info['email']}")

            st.divider()

            # Edit Startup Form
            if (
                "map_data" in st.session_state
                and "last_object_clicked_tooltip" in st.session_state["map_data"]
                and st.session_state["map_data"]["last_object_clicked_tooltip"]
                is not None
            ):
                with st.expander("Edit Startup Info"):
                    c_name = st.session_state["map_data"]["last_object_clicked_tooltip"]
                    with st.form("Edit Startup"):
                        name = st.text_input(
                            label="Name",
                            value=c_name,
                        )
                        company = find_company(c_name)
                        description = st.text_area(
                            label="Description", value=company.Description
                        )
                        startup_year = st.number_input(
                            label="Year of founding", value=company.StartupYear
                        )
                        url = st.text_input(label="Website Url", value=company.Url)
                        linkedin = st.text_input(
                            label="LinkedIn Url", value=company.LinkedInUrl
                        )
                        logo_url = st.text_input(label="Logo Url", value=company.Logo)
                        # lat = st.text_input(label="Office Latitude", value=company.Lat)
                        # lon = st.text_input(label="Office Longitude", value=company.Lon)
                        address = st.text_input(label="Address", value=company.Address)
                        city = st.text_input(label="City", value=company.City)
                        state = st.text_input(label="State", value=company.State)
                        zip_code = st.text_input(
                            label="Zip Code", value=company.ZipCode
                        )

                        logging.debug(f"tags: {company.Tags}")

                        associated_tags = st.multiselect(
                            label="Tags",
                            options=sorted_tags(),
                            default=company.Tags,
                        )

                        st.markdown("**Note:** Click off pin to reset")

                        submitted = st.form_submit_button(
                            label="Save Edit",
                            type="primary",
                        )
                        if submitted:
                            try:
                                new_company = Company(
                                    UUID=company.UUID,
                                    Name=name,
                                    Description=description,
                                    StartupYear=startup_year,
                                    Url=url,
                                    LinkedInUrl=linkedin,
                                    Logo=logo_url,
                                    Address=address,
                                    City=city,
                                    State=state,
                                    ZipCode=zip_code,
                                    Tags=associated_tags,
                                )
                                update_company(company, new_company)
                                st.success(
                                    f'Successfully updated Startup named "{name}"'
                                )
                            except Exception as e:
                                logging.error(e)
                                st.error("Error updating startup")

                        delete_button = st.form_submit_button(
                            "Delete Startup",
                            type="secondary",
                        )
                        if delete_button:
                            try:
                                delete_company(company.UUID)
                            except Exception as e:
                                logging.error(e)
                                st.error("Error deleting startup")

                st.divider()

            with st.expander("Add New Startup"):
                # Form for new startup
                with st.form("Add New Startup", clear_on_submit=False):
                    name = st.text_input(label="Name", value="test")
                    description = st.text_area(label="Description")
                    startup_year = st.number_input(
                        label="Year of founding",
                        value=datetime.now().year,
                    )
                    url = st.text_input(label="Website Url", value="test.com")
                    linkedin = st.text_input(label="LinkedIn Url")
                    logo_url = st.text_input(label="Logo Url")
                    address = st.text_input(label="Address", value="12960 Cree Drive")
                    city = st.text_input(label="City", value="San Diego")
                    state = st.text_input(label="State", value="CA")
                    zipcode = st.text_input(label="Zipcode", value="92064")
                    associated_tags = st.multiselect(
                        label="Tags",
                        options=st.session_state["tags"],
                    )

                    new_submission = st.form_submit_button(
                        label="Create",
                        args=[
                            name,
                            description,
                            startup_year,
                            url,
                            linkedin,
                            logo_url,
                            address,
                            city,
                            state,
                            zipcode,
                            associated_tags,
                        ],
                        type="primary",
                    )
                    if new_submission:
                        try:
                            new_company = Company(
                                Name=name,
                                Description=description,
                                StartupYear=startup_year,
                                Url=url,
                                LinkedInUrl=linkedin,
                                Logo=logo_url,
                                Address=address,
                                City=city,
                                State=state,
                                ZipCode=zipcode,
                                Tags=associated_tags,
                            )
                            add_company(new_company)
                            st.success("New startup added!")
                        except Exception as e:
                            st.error(e)

            st.divider()

            # Sign out
            st.button(
                label="Sign Out", on_click=auth_functions.sign_out, type="primary"
            )

            # Delete Account
            # st.header("Delete account:")
            # password = st.text_input(label="Confirm your password", type="password")
            # st.button(
            #     label="Delete Account",
            #     on_click=auth_functions.delete_account,
            #     args=[password],
            #     type="primary",
            # )
