import streamlit as st
import base64
import warnings
import pandas as pd
import numpy as np
from Quiz_utils import *
from Data import *


def show_quiz_content(all_questions):
    question_id = st.session_state.current_question
    question_data = all_questions[all_questions['ID'] == question_id].iloc[0]

    is_q = False

    if question_data.empty:
        st.write("No question available")
        return
    
    question_text = question_data['Question']
    question_section = question_data['Section']
    question_example = question_data['Example']
    question_info = question_data['Information']
    question_resources = question_data['Resources']


    response = st.session_state.responses.get(question_id, "")

    highlighted_text = question_text
    glossary_terms = sorted(terms_definitions.keys(), key=lambda term: len(term), reverse=True)

    for term in glossary_terms:
        if term.lower() in highlighted_text.lower():
            term_start = highlighted_text.lower().find(term.lower())
            termd = highlighted_text[term_start:term_start + len(term)]
            highlighted_text = highlighted_text.replace(termd, f"<span style='color:{st.get_option('theme.primaryColor')}'>{termd}</span>")

    st.markdown(
    f"<h3 style='color: {st.get_option('theme.primaryColor')}; font-weight: bold;'>{question_section}</h3>",
    unsafe_allow_html=True
    )
    st.markdown(f"## {highlighted_text}", unsafe_allow_html=True)

    if question_example:
        st.write(f"{question_example}")

    response = st.text_input("Answer:", value=response, key=f"text_{question_id}")

    progress = (question_id / len(all_questions)) 
    st.progress(progress)
    col1, col2, col3 = st.columns([1, 1, 1])


    with col1:
        if st.button("Previous"):
            prev_question_ID = get_previous_question()
            if prev_question_ID:
                st.session_state.current_question = prev_question_ID
                st.rerun()
            else:
                st.warning("No previous question")
            
    with col2:
        # create a dict, key: question_id, value1 = response, value2 = question_text
        stop = False
        if response:
            st.session_state.QA[question_id] = {"Question": question_text, "Answer": response}
            
            next_question_ID, stop = get_n_questions()
            st.session_state.unable_next = False
            is_q = True
        if stop:
            st.session_state.unable_submit = False
            st.session_state.unable_next = True
        if st.button("Next", disabled= False):
                    if not response or response == "":
                            st.warning("Please provide an answer before proceeding!")
                    elif stop:
                        st.warning("This is the last question. Please submit or revise your answers.")
                    else:
                            st.session_state.current_question = next_question_ID
                            st.session_state.responses[question_id] = response
                            st.session_state.history.append(question_id)
                            st.session_state.expanders_state = {'information': False, 'resources': False, 'glossary': False}
                            st.session_state.unable_next = True
                            st.rerun()
                        
    with col3:
        if st.button("Submit", disabled= st.session_state.unable_submit):
                if not response:
                    st.warning("Please provide an answer before submitting!")
                else:
                    st.session_state.responses[question_id] = response
                    st.session_state.submitted = True
                    st.rerun()


        

    with st.expander("Information", expanded= True):
        st.write(question_info)

    with st.expander("Resources", expanded=st.session_state.expanders_state['resources']):
        st.write(question_resources)
    return
