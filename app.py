import streamlit as st
import sys
from io import StringIO
import pandas as pd
import time

sys.path.append('src')
from src.main import main

# Initialize session state
if 'running' not in st.session_state:
    st.session_state.running = False
if 'stop_requested' not in st.session_state:
    st.session_state.stop_requested = False

# Create buttons at the top
col1, col2, col3 = st.columns(3)

with col1:
    if st.button('▶ Run', disabled=st.session_state.running, use_container_width=True):
        st.session_state.running = True
        st.session_state.stop_requested = False
        st.rerun()

with col2:
    if st.button('◼ Stop', disabled=not st.session_state.running, use_container_width=True):
        st.session_state.stop_requested = True
        st.session_state.running = False
        st.rerun()

with col3:
    if st.button('🗘 Restart', use_container_width=True):
        st.session_state.stop_requested = True
        st.session_state.running = False
        time.sleep(0.1)
        st.session_state.running = True
        st.session_state.stop_requested = False
        st.rerun()

# Create a status container
status_container = st.empty()

# Create placeholders
output_placeholder = st.empty()
df_placeholders = [st.empty() for _ in range(10)]

# Only run if the running flag is set
if st.session_state.running:
    # Clear all placeholders at start of each run
    output_placeholder.empty()
    for placeholder in df_placeholders:
        placeholder.empty()

    # CRITICAL: Reset collected data on each run (use local variables, not session state)
    collected_dataframes = []
    output_buffer = StringIO()

    original_stdout = sys.stdout
    sys.stdout = output_buffer
    
    import builtins
    original_print = builtins.print

    def custom_print(*args, **kwargs):
        # Check if stop was requested
        if st.session_state.stop_requested:
            raise KeyboardInterrupt("Process stopped by user")
        
        for arg in args:
            if isinstance(arg, pd.DataFrame):
                # Create a copy to avoid reference issues
                collected_dataframes.append(arg.copy())
            else:
                original_print(arg, **kwargs, file=output_buffer)
        
        # Update display - clear first to avoid duplicates
        output_placeholder.empty()
        output_placeholder.markdown(output_buffer.getvalue())
        
        # Clear and update dataframes
        for i in range(len(df_placeholders)):
            df_placeholders[i].empty()
        
        for i, df in enumerate(collected_dataframes):
            if i < len(df_placeholders):
                df_placeholders[i].dataframe(df, height=400, use_container_width=True, key=f"df_{i}_{id(df)}")

    builtins.print = custom_print

    # Show loading indicator
    with status_container:
        with st.spinner('📈 Processing stonks...'):
            try:
                main()
                status_container.success('✅ Processing complete!')
                st.session_state.running = False
            except KeyboardInterrupt:
                status_container.warning('◼ Process stopped by user')
                st.session_state.running = False
            except Exception as e:
                status_container.error(f'❌ Error: {str(e)}')
                st.session_state.running = False
                import traceback
                st.error(traceback.format_exc())
            finally:
                sys.stdout = original_stdout
                builtins.print = original_print
else:
    # Clear everything when not running
    output_placeholder.empty()
    for placeholder in df_placeholders:
        placeholder.empty()
    status_container.info('👆 Click "Run" to start processing trades')