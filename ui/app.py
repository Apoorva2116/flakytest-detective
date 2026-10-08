import json
import os
import sys

import pandas as pd
import streamlit as st


# =========================================================
# PATHS
# =========================================================

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

RESULTS_DIR = os.path.join(
    ROOT,
    "results"
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="FlakyTest Detective",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# STYLING
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .app-subtitle {
        color: #9ca3af;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    .info-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #30363d;
        background: #161b22;
    }

    .pipeline-box {
        padding: 1rem;
        border-radius: 8px;
        background: #161b22;
        border: 1px solid #30363d;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATA HELPERS
# =========================================================

def load_json(filename):

    path = os.path.join(
        RESULTS_DIR,
        filename
    )

    if not os.path.exists(path):
        return {}

    try:

        with open(
            path,
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


def load_history():

    return load_json(
        "history.json"
    )


def load_ground_truth():

    return load_json(
        "ground_truth.json"
    )


def load_rag_results():

    candidates = [
        "llm_phi3:mini_rag.json",
        "llm_phi3_mini_rag.json"
    ]

    for filename in candidates:

        data = load_json(
            filename
        )

        if data:
            return data

    return {}


def load_norag_results():

    candidates = [
        "llm_phi3:mini_norag.json",
        "llm_phi3_mini_norag.json"
    ]

    for filename in candidates:

        data = load_json(
            filename
        )

        if data:
            return data

    return {}


# =========================================================
# LOAD EXISTING RESULTS
# =========================================================

history = load_history()
ground_truth = load_ground_truth()
rag_results = load_rag_results()
norag_results = load_norag_results()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    "## 🔍 FlakyTest Detective"
)

st.sidebar.caption(
    "AI-powered CI/CD failure triage"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Test Analysis",
        "RAG Evidence",
        "CI/CD",
        "Upload Project"
    ]
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "RAG • LLM • Guardrails • Docker"
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="app-title">🔍 FlakyTest Detective</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="app-subtitle">'
    'AI-powered CI/CD failure triage using '
    'RAG, LLM reasoning and guardrails'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.header("Project Dashboard")

    total_tests = 118

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Benchmark Tests",
            total_tests
        )

    with c2:

        st.metric(
            "Ground-Truth Flaky",
            39
        )

    with c3:

        st.metric(
            "Stable",
            65
        )

    with c4:

        st.metric(
            "Real Bugs",
            14
        )

    st.markdown("---")

    st.subheader(
        "Model Evaluation"
    )

    benchmark = pd.DataFrame(
        [
            {
                "Method": "Rerun Once",
                "Precision": 1.00,
                "Recall": 0.21,
                "F1": 0.34
            },
            {
                "Method": "Failed in History",
                "Precision": 0.70,
                "Recall": 0.85,
                "F1": 0.77
            },
            {
                "Method": "Phi-3 Mini — No RAG",
                "Precision": 0.80,
                "Recall": 0.85,
                "F1": 0.83
            },
            {
                "Method": "Phi-3 Mini — RAG",
                "Precision": 0.72,
                "Recall": 0.85,
                "F1": 0.78
            },
            {
                "Method": "CodeLlama — RAG",
                "Precision": 0.33,
                "Recall": 1.00,
                "F1": 0.50
            }
        ]
    )

    display_table = benchmark.copy()

    for column in [
        "Precision",
        "Recall",
        "F1"
    ]:

        display_table[column] = (
            display_table[column]
            .map(
                lambda x: f"{x:.2f}"
            )
        )

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader(
        "F1 Score Comparison"
    )

    chart_data = benchmark.set_index(
        "Method"
    )["F1"]

    st.bar_chart(
        chart_data
    )

    st.info(
        "Key finding: Phi-3 Mini without retrieval "
        "achieved the strongest F1 score (0.83) in the "
        "current benchmark. RAG maintained recall but "
        "increased false positives in this configuration."
    )

    st.markdown("---")

    st.subheader(
        "System Architecture"
    )

    cols = st.columns(5)

    pipeline = [
        "GitHub Actions",
        "Docker",
        "pytest",
        "RAG + ChromaDB",
        "LLM + Guardrails"
    ]

    for col, item in zip(
        cols,
        pipeline
    ):

        with col:

            st.markdown(
                f"""
                <div class="pipeline-box">
                ✓ {item}
                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# TEST ANALYSIS
# =========================================================

elif page == "Test Analysis":

    st.header(
        "🔬 Test Analysis"
    )

    if not history:

        st.error(
            "history.json could not be found."
        )

    else:

        test_names = list(
            history.get(
                "tests",
                {}
            ).keys()
        )

        selected = st.selectbox(
            "Select a test",
            test_names
        )

        test_history = history[
            "tests"
        ].get(
            selected,
            {}
        )

        old_result = rag_results.get(
            selected,
            {}
        )

        st.markdown("---")

        st.subheader(
            "Execution History"
        )

        results_list = test_history.get(
            "results",
            []
        )

        messages = test_history.get(
            "msgs",
            []
        )

        h1, h2, h3 = st.columns(3)

        with h1:

            st.metric(
                "Recent Runs",
                len(results_list)
            )

        with h2:

            failures = results_list.count(
                0
            )

            st.metric(
                "Failures",
                failures
            )

        with h3:

            passes = results_list.count(
                1
            )

            st.metric(
                "Passes",
                passes
            )

        if messages:

            st.write(
                "**Recent failure message:**"
            )

            st.code(
                messages[0]
            )

        st.markdown("---")

        st.subheader(
            "Stored Benchmark Result"
        )

        old_flaky = old_result.get(
            "flaky"
        )

        if old_flaky is True:

            st.warning(
                "Benchmark prediction: FLAKY"
            )

        elif old_flaky is False:

            st.success(
                "Benchmark prediction: STABLE"
            )

        if old_result.get(
            "reason"
        ):

            st.write(
                old_result["reason"]
            )

        st.markdown("---")

        st.subheader(
            "Live AI Analysis"
        )

        st.write(
            "Run this individual test through the "
            "current RAG + Phi-3 + guardrails pipeline."
        )

        if st.button(
            "🚀 Analyze with AI",
            type="primary"
        ):

            with st.spinner(
                "Running RAG + Phi-3 analysis..."
            ):

                try:

                    from rag.run_judge import (
                        test_sources,
                        build_index,
                        build_prompt,
                        ask,
                        parse
                    )

                    from pipeline.guardrails import (
                        validate_input,
                        validate_output,
                        fallback_classification
                    )

                    sources = test_sources()

                    code = sources[
                        selected
                    ]

                    input_check = validate_input(
                        test_name=selected,
                        test_code=code,
                        history=test_history
                    )

                    if not input_check[
                        "valid"
                    ]:

                        st.error(
                            "Input guardrail failed."
                        )

                        st.json(
                            input_check
                        )

                    else:

                        collection = build_index(
                            history
                        )

                        query = (
                            code
                            + " "
                            + " ".join(
                                messages[:1]
                            )
                        )

                        hits = collection.query(
                            query_texts=[
                                query
                            ],
                            n_results=3
                        )[
                            "documents"
                        ][0]

                        context = (
                            "Retrieved context:\n- "
                            + "\n- ".join(
                                hits
                            )
                        )

                        prompt = build_prompt(
                            code=code,
                            test_history=test_history,
                            context=context
                        )

                        text, seconds = ask(
                            "phi3:mini",
                            prompt
                        )

                        parsed = parse(
                            text
                        )

                        output_check = (
                            validate_output(
                                parsed
                            )
                        )

                        if output_check[
                            "valid"
                        ]:

                            result = (
                                output_check[
                                    "result"
                                ]
                            )

                        else:

                            result = (
                                fallback_classification(
                                    test_history
                                )
                            )

                        classification = result.get(
                            "classification"
                        )

                        confidence = float(
                            result.get(
                                "confidence",
                                0
                            )
                        )

                        if classification == "FLAKY":

                            st.warning(
                                f"⚠️ FLAKY — "
                                f"{confidence:.0%} confidence"
                            )

                        elif classification == "REAL_BUG":

                            st.error(
                                f"🐞 REAL BUG — "
                                f"{confidence:.0%} confidence"
                            )

                        elif classification == "STABLE":

                            st.success(
                                f"✓ STABLE — "
                                f"{confidence:.0%} confidence"
                            )

                        else:

                            st.info(
                                "🔎 NEEDS REVIEW"
                            )

                        a, b = st.columns(2)

                        with a:

                            st.metric(
                                "Confidence",
                                f"{confidence:.0%}"
                            )

                        with b:

                            st.metric(
                                "Analysis Time",
                                f"{seconds:.1f}s"
                            )

                        st.subheader(
                            "AI Reasoning"
                        )

                        st.write(
                            result.get(
                                "reason",
                                ""
                            )
                        )

                        st.subheader(
                            "Retrieved Evidence"
                        )

                        evidence = result.get(
                            "evidence",
                            []
                        )

                        if evidence:

                            for item in evidence:

                                st.markdown(
                                    f"• {item}"
                                )

                        else:

                            for item in hits:

                                st.markdown(
                                    f"• {item}"
                                )

                except Exception as e:

                    st.error(
                        "Live analysis failed."
                    )

                    st.exception(
                        e
                    )


# =========================================================
# RAG EVIDENCE
# =========================================================

elif page == "RAG Evidence":

    st.header(
        "📚 RAG Evidence"
    )

    st.info(
        "The benchmark result files were generated before "
        "the evidence field was added. Use Test Analysis → "
        "Analyze with AI to generate fresh retrieved evidence."
    )

    if history:

        names = list(
            history.get(
                "tests",
                {}
            ).keys()
        )

        selected = st.selectbox(
            "Select a test",
            names
        )

        st.subheader(
            "Stored RAG Result"
        )

        result = rag_results.get(
            selected,
            {}
        )

        if result:

            st.write(
                result.get(
                    "reason",
                    "No reason stored."
                )
            )

        st.markdown("---")

        st.subheader(
            "RAG Knowledge Sources"
        )

        sources = [
            "Randomness",
            "Timing",
            "Hash ordering",
            "Wall clock",
            "Network/service",
            "Order dependence/shared state",
            "Deterministic real failure"
        ]

        for source in sources:

            st.markdown(
                f"• {source}"
            )


# =========================================================
# CI/CD
# =========================================================

elif page == "CI/CD":

    st.header(
        "⚙️ Intelligent CI/CD"
    )

    st.write(
        "FlakyTest Detective integrates AI-based "
        "failure triage into the software delivery pipeline."
    )

    st.markdown("---")

    steps = [
        (
            "1",
            "Developer Push",
            "Code is pushed to the repository."
        ),
        (
            "2",
            "GitHub Actions",
            "CI workflow starts automatically."
        ),
        (
            "3",
            "Docker",
            "Tests execute in a reproducible environment."
        ),
        (
            "4",
            "pytest",
            "Test execution and failure information are collected."
        ),
        (
            "5",
            "Input Guardrails",
            "Test input and history are validated."
        ),
        (
            "6",
            "ChromaDB RAG",
            "Relevant testing knowledge and history are retrieved."
        ),
        (
            "7",
            "Phi-3 Mini",
            "The LLM classifies the failure."
        ),
        (
            "8",
            "Output Guardrails",
            "The model response is validated."
        ),
        (
            "9",
            "Final Classification",
            "FLAKY / REAL_BUG / STABLE / NEEDS_REVIEW."
        )
    ]

    for number, title, description in steps:

        st.markdown(
            f"""
            <div class="info-card">
            <b>{number}. {title}</b><br>
            <span style="color:#9ca3af">
            {description}
            </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")


# =========================================================
# UPLOAD PROJECT
# =========================================================

elif page == "Upload Project":

    st.header(
        "📦 Upload Python Test Project"
    )

    st.write(
        "Upload a ZIP containing a Python/pytest project."
    )

    uploaded = st.file_uploader(
        "Choose a ZIP file",
        type=["zip"]
    )

    if uploaded:

        st.success(
            f"Uploaded: {uploaded.name}"
        )

        st.write(
            f"File size: "
            f"{uploaded.size / 1024:.1f} KB"
        )

        st.markdown("---")

        st.warning(
            "For security, uploaded code should be "
            "executed only inside an isolated Docker "
            "environment."
        )

        if st.button(
            "🚀 Prepare Analysis"
        ):

            st.info(
                "Upload received. Docker-isolated "
                "execution will be connected to the "
                "analysis engine."
            )

            st.code(
                "Upload → Docker → pytest → RAG → LLM → Guardrails"
            )
