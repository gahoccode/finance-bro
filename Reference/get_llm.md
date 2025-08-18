def get_llm():
    st.sidebar.header("Select a LLM", divider='rainbow')
    llm = st.sidebar.radio("Choose a llm:",
                           ("OpenAI",
                            "Google Gemini")
                           )
    return llm

if addon:
            llm = get_llm()
if llm == "OpenAI"
elif llm == "Google Gemini"
llm=
