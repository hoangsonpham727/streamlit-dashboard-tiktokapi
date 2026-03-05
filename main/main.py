import streamlit as st

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
)

from streamlit_option_menu import option_menu

# Import pages after set_page_config so module-level code doesn't fire first
import home, chat, about


class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        
        #Customise the sidebar
        with st.sidebar:        
            app = option_menu(
                menu_title='Data Analysis ',
                options=['Home','ChatBot','About'],
                icons=['house-fill','chat-fill','info-circle-fill'],
                menu_icon='chat-text-fill',
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": "#10131c"},
                    "icon": {"color": "#c9d1e0", "font-size": "20px"},
                    "nav-link": {"color": "#c9d1e0", "font-size": "16px", "text-align": "left", "margin": "2px 0", "--hover-color": "#1c2033", "border-radius": "8px"},
                    "nav-link-selected": {"background-color": "#0068C9", "color": "#ffffff", "font-weight": "600"},
                    "menu-title": {"color": "#8892a4", "font-size": "13px", "font-weight": "600", "letter-spacing": "0.06em"},
                }
                )

        
        if app == "Home":
            home.app()
        if app == "ChatBot":
            chat.app()    
        if app == 'About':
            about.app()    
             
          
            
    run()            
         