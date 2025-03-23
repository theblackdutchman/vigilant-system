import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, callback, dash_table, State, ctx
import base64
import io
from dash.exceptions import PreventUpdate
import random
import string

# Read the data
df = pd.read_excel('Complete_Hospital_Locations_and_Sizes.xlsx')

# Process the data
# Fill missing size categories with 'N/A'
df['Size Category'] = df['Size Category'].fillna('N/A')

# Process specialties
def extract_primary_specialty(specialty_str):
    if not isinstance(specialty_str, str) or not specialty_str.strip():
        return 'N/A'
    specialties = [s.strip() for s in specialty_str.split(',')]
    return specialties[0] if specialties else 'N/A'

df['Primary Specialty'] = df['Specialties'].apply(extract_primary_specialty)

# Count hospitals by size
size_counts = df['Size Category'].value_counts()
small_count = size_counts.get('Small', 0)
medium_count = size_counts.get('Medium', 0)
large_count = size_counts.get('Large', 0)
na_count = size_counts.get('N/A', 0)

# Calculate average beds
avg_beds = df['Estimated Beds'].mean()

# Get top specialties
specialty_counts = df['Primary Specialty'].value_counts()
top_specialties = specialty_counts.head(5)
other_count = specialty_counts[5:].sum() if len(specialty_counts) > 5 else 0

# Get unique specialties and sizes for dropdowns
unique_specialties = sorted(df['Primary Specialty'].unique())
unique_sizes = sorted(df['Size Category'].unique())

# Generate a random letter for each hospital (for company card display)
def random_letter():
    return random.choice(string.ascii_uppercase)

df['Initial'] = [random_letter() for _ in range(len(df))]

# Encode the logo
with open('_eo_scale_yourself.png', 'rb') as image_file:
    encoded_logo = base64.b64encode(image_file.read()).decode('ascii')

# Initialize the Dash app
app = Dash(__name__, title='Hospital Dashboard', suppress_callback_exceptions=True)

# Define the layout
app.layout = html.Div([
    # Store the current page
    dcc.Store(id='current-page', data='summary'),
    
    # Main container with sidebar and content
    html.Div([
        # Sidebar
        html.Div([
            # Logo and title
            html.Div([
                html.Img(src=f'data:image/png;base64,{encoded_logo}', 
                         style={'height': '30px', 'marginRight': '10px'}),
                html.H2('AI Insights', style={'color': 'white', 'margin': '0'})
            ], style={'display': 'flex', 'alignItems': 'center', 'padding': '20px 15px', 
                      'borderBottom': '1px solid rgba(255,255,255,0.1)'}),
            
            # DASHBOARD section
            html.Div([
                html.H3('DASHBOARD', style={'color': 'rgba(255,255,255,0.5)', 'fontSize': '14px', 
                                           'letterSpacing': '1px', 'padding': '20px 15px 10px 15px', 
                                           'margin': '0'}),
                
                # Summary link
                html.Div([
                    html.I(className="fas fa-chart-pie", style={'marginRight': '10px', 'color': 'white'}),
                    html.Span('Summary', style={'color': 'white'})
                ], id='summary-link', className='sidebar-link', n_clicks=0,
                   style={'padding': '10px 15px', 'display': 'flex', 'alignItems': 'center',
                          'cursor': 'pointer', 'backgroundColor': 'rgba(255,255,255,0.1)'}),
                
                # Companies link
                html.Div([
                    html.I(className="fas fa-building", style={'marginRight': '10px', 'color': 'white'}),
                    html.Span('Companies', style={'color': 'white'})
                ], id='companies-link', className='sidebar-link', n_clicks=0,
                   style={'padding': '10px 15px', 'display': 'flex', 'alignItems': 'center',
                          'cursor': 'pointer'}),
                
                # Map View link
                html.Div([
                    html.I(className="fas fa-map-marker-alt", style={'marginRight': '10px', 'color': 'white'}),
                    html.Span('Map View', style={'color': 'white'})
                ], id='map-link', className='sidebar-link', n_clicks=0,
                   style={'padding': '10px 15px', 'display': 'flex', 'alignItems': 'center',
                          'cursor': 'pointer'}),
                
                # Analytics link
                html.Div([
                    html.I(className="fas fa-chart-line", style={'marginRight': '10px', 'color': 'white'}),
                    html.Span('Analytics', style={'color': 'white'})
                ], id='analytics-link', className='sidebar-link', n_clicks=0,
                   style={'padding': '10px 15px', 'display': 'flex', 'alignItems': 'center',
                          'cursor': 'pointer'})
            ]),
            
            # DATA section
            html.Div([
                html.H3('DATA', style={'color': 'rgba(255,255,255,0.5)', 'fontSize': '14px', 
                                      'letterSpacing': '1px', 'padding': '20px 15px 10px 15px', 
                                      'margin': '0'}),
                
                # Table View link
                html.Div([
                    html.I(className="fas fa-table", style={'marginRight': '10px', 'color': 'white'}),
                    html.Span('Table View', style={'color': 'white'})
                ], id='table-link', className='sidebar-link', n_clicks=0,
                   style={'padding': '10px 15px', 'display': 'flex', 'alignItems': 'center',
                          'cursor': 'pointer'})
            ])
        ], style={'width': '250px', 'backgroundColor': '#4e73df', 'minHeight': '100vh', 
                  'boxShadow': '0 2px 5px rgba(0,0,0,0.1)', 'position': 'fixed', 'top': '0', 'left': '0'}),
        
        # Main content
        html.Div([
            # Content will be loaded here based on the selected page
            html.Div(id='page-content', style={'padding': '20px'})
        ], style={'marginLeft': '250px', 'width': 'calc(100% - 250px)', 'minHeight': '100vh'})
    ])
])

# Callback to update active link style
@app.callback(
    [Output('summary-link', 'style'),
     Output('companies-link', 'style'),
     Output('map-link', 'style'),
     Output('analytics-link', 'style'),
     Output('table-link', 'style')],
    [Input('current-page', 'data')]
)
def update_active_link(current_page):
    base_style = {'padding': '10px 15px', 'display': 'flex', 'alignItems': 'center',
                 'cursor': 'pointer'}
    active_style = {**base_style, 'backgroundColor': 'rgba(255,255,255,0.1)'}
    
    styles = [base_style.copy() for _ in range(5)]
    
    if current_page == 'summary':
        styles[0] = active_style
    elif current_page == 'companies':
        styles[1] = active_style
    elif current_page == 'map':
        styles[2] = active_style
    elif current_page == 'analytics':
        styles[3] = active_style
    elif current_page == 'table':
        styles[4] = active_style
    
    return styles

# Callback to update current page
@app.callback(
    Output('current-page', 'data'),
    [Input('summary-link', 'n_clicks'),
     Input('companies-link', 'n_clicks'),
     Input('map-link', 'n_clicks'),
     Input('analytics-link', 'n_clicks'),
     Input('table-link', 'n_clicks')],
    [State('current-page', 'data')],
    prevent_initial_call=True
)
def update_current_page(summary_clicks, companies_clicks, map_clicks, analytics_clicks, table_clicks, current):
    triggered_id = ctx.triggered_id
    if triggered_id == 'summary-link':
        return 'summary'
    elif triggered_id == 'companies-link':
        return 'companies'
    elif triggered_id == 'map-link':
        return 'map'
    elif triggered_id == 'analytics-link':
        return 'analytics'
    elif triggered_id == 'table-link':
        return 'table'
    return current  # Default

# Callback to render page content
@app.callback(
    Output('page-content', 'children'),
    [Input('current-page', 'data')]
)
def render_page_content(page):
    if page == 'summary':
        return render_summary_page()
    elif page == 'companies':
        return render_companies_page()
    elif page == 'map':
        return render_map_page()
    elif page == 'analytics':
        return render_analytics_page()
    elif page == 'table':
        return render_table_page()
    return render_summary_page()  # Default

# Summary page content
def render_summary_page():
    return html.Div([
        # Page title
        html.H1('Hospital Dashboard', style={'margin': '0 0 20px 0'}),
        
        # Description
        html.P('A comprehensive overview of hospitals across the United States.', 
               style={'marginBottom': '20px'}),
        
        # Top cards
        html.Div([
            # Total Companies
            html.Div([
                html.H4('TOTAL COMPANIES', style={'color': '#6c757d', 'fontSize': '14px', 'margin': '0'}),
                html.H2(f'{len(df)}', style={'margin': '10px 0', 'color': '#212529'}),
                html.I(className="fas fa-building", style={'fontSize': '24px', 'color': '#6c757d'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': 'white', 
                      'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 
                      'margin': '0 10px', 'minWidth': '150px'}),
            
            # Small Hospitals
            html.Div([
                html.H4('SMALL HOSPITALS', style={'color': '#6c757d', 'fontSize': '14px', 'margin': '0'}),
                html.H2(f'{small_count}', style={'margin': '10px 0', 'color': '#212529'}),
                html.I(className="fas fa-clinic-medical", style={'fontSize': '24px', 'color': '#6c757d'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': 'white', 
                      'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 
                      'margin': '0 10px', 'minWidth': '150px'}),
            
            # Medium Hospitals
            html.Div([
                html.H4('MEDIUM HOSPITALS', style={'color': '#6c757d', 'fontSize': '14px', 'margin': '0'}),
                html.H2(f'{medium_count}', style={'margin': '10px 0', 'color': '#212529'}),
                html.I(className="fas fa-hospital", style={'fontSize': '24px', 'color': '#6c757d'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': 'white', 
                      'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 
                      'margin': '0 10px', 'minWidth': '150px'}),
            
            # Large Hospitals
            html.Div([
                html.H4('LARGE HOSPITALS', style={'color': '#6c757d', 'fontSize': '14px', 'margin': '0'}),
                html.H2(f'{large_count}', style={'margin': '10px 0', 'color': '#212529'}),
                html.I(className="fas fa-hospital-alt", style={'fontSize': '24px', 'color': '#6c757d'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': 'white', 
                      'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 
                      'margin': '0 10px', 'minWidth': '150px'}),
            
            # Average Beds
            html.Div([
                html.H4('AVERAGE BEDS', style={'color': '#6c757d', 'fontSize': '14px', 'margin': '0'}),
                html.H2(f'{avg_beds:.0f}', style={'margin': '10px 0', 'color': '#212529'}),
                html.I(className="fas fa-bed", style={'fontSize': '24px', 'color': '#6c757d'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': 'white', 
                      'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 
                      'margin': '0 10px', 'minWidth': '150px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between', 
                  'margin': '0 0 20px 0'}),
        
        # Charts row
        html.Div([
            # Companies by Size
            html.Div([
                html.H3('Companies by Size', style={'padding': '15px', 'margin': '0', 
                                                   'borderBottom': '1px solid #ddd'}),
                dcc.Graph(
                    id='size-chart',
                    figure=px.bar(
                        x=['Small', 'Medium', 'Large', 'N/A'],
                        y=[small_count, medium_count, large_count, na_count],
                        labels={'x': 'Size Category', 'y': 'Number of Hospitals'},
                        color_discrete_sequence=['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e']
                    ).update_layout(
                        margin=dict(l=40, r=40, t=40, b=40),
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        height=400
                    )
                )
            ], style={'flex': '1', 'backgroundColor': 'white', 'borderRadius': '5px', 
                      'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'margin': '0 10px', 
                      'minWidth': '45%'}),
            
            # Specialty Focus
            html.Div([
                html.H3('Specialty Focus', style={'padding': '15px', 'margin': '0', 
                                                 'borderBottom': '1px solid #ddd'}),
                dcc.Graph(
                    id='specialty-chart',
                    figure=px.pie(
                        values=list(top_specialties) + [other_count],
                        names=list(top_specialties.index) + ['Other'],
                        hole=0.4,
                        color_discrete_sequence=['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#f8f9fa']
                    ).update_layout(
                        margin=dict(l=40, r=40, t=40, b=40),
                        paper_bgcolor='white',
                        height=400
                    )
                )
            ], style={'flex': '1', 'backgroundColor': 'white', 'borderRadius': '5px', 
                      'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'margin': '0 10px', 
                      'minWidth': '45%'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between', 
                  'margin': '0 0 20px 0'})
    ])

# Create a company card component
def create_company_card(hospital):
    # Generate a random founding year between 2015 and 2024
    founding_year = random.randint(2015, 2024)
    
    # Generate a random description based on hospital type and specialty
    descriptions = [
        f"{hospital['Hospital/Organization']} is a leading healthcare provider specializing in {hospital['Primary Specialty']}.",
        f"{hospital['Hospital/Organization']} provides exceptional care with a focus on {hospital['Primary Specialty']}.",
        f"{hospital['Hospital/Organization']} is revolutionizing healthcare in {hospital['Location']} with innovative approaches to {hospital['Primary Specialty']}.",
        f"{hospital['Hospital/Organization']} is dedicated to improving patient outcomes through advanced {hospital['Primary Specialty']} treatments."
    ]
    description = random.choice(descriptions)
    
    # Determine badge color based on size
    badge_color = {
        'Small': '#1cc88a',
        'Medium': '#4e73df',
        'Large': '#e74a3b',
        'N/A': '#f6c23e'
    }.get(hospital['Size Category'], '#6c757d')
    
    return html.Div([
        # Card content
        html.Div([
            # Initial circle and hospital name
            html.Div([
                # Initial circle
                html.Div([
                    html.Span(hospital['Initial'], style={
                        'color': '#4e73df',
                        'fontWeight': 'bold',
                        'fontSize': '24px'
                    })
                ], style={
                    'backgroundColor': '#f8f9fa',
                    'borderRadius': '50%',
                    'width': '60px',
                    'height': '60px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'marginBottom': '15px'
                }),
                
                # Hospital name
                html.H3(hospital['Hospital/Organization'][:25] + ('...' if len(hospital['Hospital/Organization']) > 25 else ''), 
                        style={'fontSize': '18px', 'margin': '10px 0'})
            ], style={'textAlign': 'center', 'marginBottom': '15px'}),
            
            # Badges for size and location
            html.Div([
                # Size badge
                html.Span(hospital['Size Category'], style={
                    'backgroundColor': badge_color,
                    'color': 'white',
                    'padding': '5px 10px',
                    'borderRadius': '15px',
                    'fontSize': '12px',
                    'marginRight': '5px',
                    'display': 'inline-block',
                    'marginBottom': '5px'
                }),
                
                # Location badge
                html.Span(hospital['Location'], style={
                    'backgroundColor': '#4e73df',
                    'color': 'white',
                    'padding': '5px 10px',
                    'borderRadius': '15px',
                    'fontSize': '12px',
                    'display': 'inline-block',
                    'marginBottom': '5px'
                })
            ], style={'marginBottom': '15px'}),
            
            # Description
            html.P(description[:120] + ('...' if len(description) > 120 else ''), 
                   style={'fontSize': '14px', 'color': '#6c757d', 'marginBottom': '15px', 'height': '60px'}),
            
            # Founded year and visit button
            html.Div([
                html.Div([
                    html.Span('Founded: ', style={'fontWeight': 'bold'}),
                    html.Span(str(founding_year))
                ], style={'display': 'inline-block', 'marginTop': '8px'}),
                
                html.Button('Visit', style={
                    'backgroundColor': 'white',
                    'color': '#4e73df',
                    'border': '1px solid #4e73df',
                    'borderRadius': '4px',
                    'padding': '5px 15px',
                    'cursor': 'pointer',
                    'float': 'right'
                })
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'})
        ], style={'padding': '20px'})
    ], style={
        'backgroundColor': 'white',
        'borderRadius': '5px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'margin': '10px',
        'width': 'calc(25% - 20px)',
        'minWidth': '250px'
    })

# Companies page content
def render_companies_page():
    # Get a sample of hospitals for display
    sample_hospitals = df.sample(min(8, len(df))).to_dict('records')
    
    return html.Div([
        # Featured Companies section
        html.Div([
            html.H2('Featured Companies', style={
                'padding': '15px',
                'margin': '0',
                'color': '#4e73df',
                'borderBottom': '1px solid #ddd'
            })
        ], style={
            'backgroundColor': 'white',
            'borderRadius': '5px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        }),
        
        # Search bar
        html.Div([
            html.Div([
                html.I(className="fas fa-search", style={
                    'position': 'absolute',
                    'left': '15px',
                    'top': '50%',
                    'transform': 'translateY(-50%)',
                    'color': '#6c757d'
                }),
                dcc.Input(
                    id='company-search',
                    type='text',
                    placeholder='Search companies...',
                    style={
                        'width': '100%',
                        'padding': '10px 10px 10px 40px',
                        'borderRadius': '5px',
                        'border': '1px solid #ddd',
                        'fontSize': '16px'
                    }
                )
            ], style={'position': 'relative', 'width': '100%'})
        ], style={
            'marginBottom': '20px'
        }),
        
        # Company cards grid
        html.Div([
            # Create a card for each hospital in the sample
            *[create_company_card(hospital) for hospital in sample_hospitals]
        ], style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'margin': '0 -10px'  # Negative margin to offset card margins
        }),
        
        # Store for filtered hospitals
        dcc.Store(id='filtered-hospitals', data=sample_hospitals)
    ])

# Callback to filter companies based on search
@app.callback(
    Output('filtered-hospitals', 'data'),
    [Input('company-search', 'value')]
)
def filter_companies(search_term):
    if not search_term:
        return df.sample(min(8, len(df))).to_dict('records')
    
    filtered = df[df['Hospital/Organization'].str.contains(search_term, case=False) | 
                  df['Location'].str.contains(search_term, case=False) |
                  df['Primary Specialty'].str.contains(search_term, case=False)]
    
    if len(filtered) == 0:
        return df.sample(min(8, len(df))).to_dict('records')
    
    return filtered.head(8).to_dict('records')

# Map page content
def render_map_page():
    return html.Div([
        html.H1('Map View', style={'margin': '0 0 20px 0'}),
        html.P('Geographic distribution of hospitals across the United States.'),
        
        # Filter controls
        html.Div([
            html.Div([
                html.Label('Filter Type:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.RadioItems(
                    id='filter-type',
                    options=[
                        {'label': 'All Hospitals', 'value': 'all'},
                        {'label': 'By Size', 'value': 'size'},
                        {'label': 'By Specialty', 'value': 'specialty'}
                    ],
                    value='all',
                    inline=True,
                    style={'marginRight': '20px'}
                )
            ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '20px'}),
            
            html.Div([
                html.Label('Size:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Dropdown(
                    id='size-dropdown',
                    options=[{'label': size, 'value': size} for size in unique_sizes],
                    value=None,
                    placeholder='Select a size',
                    style={'width': '200px'},
                    disabled=True
                )
            ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '20px'}),
            
            html.Div([
                html.Label('Specialty:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Dropdown(
                    id='specialty-dropdown',
                    options=[{'label': spec, 'value': spec} for spec in unique_specialties],
                    value=None,
                    placeholder='Select a specialty',
                    style={'width': '200px'},
                    disabled=True
                )
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'display': 'flex', 'padding': '15px', 'backgroundColor': 'white', 
                  'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 
                  'marginBottom': '20px'}),
        
        # Map
        html.Div([
            dcc.Graph(id='map-chart')
        ], style={'backgroundColor': 'white', 'borderRadius': '5px', 
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    ])

# Analytics page content
def render_analytics_page():
    # Calculate additional analytics
    beds_by_size = df.groupby('Size Category')['Estimated Beds'].mean().reset_index()
    beds_by_size = beds_by_size.sort_values('Estimated Beds', ascending=False)
    
    top_locations = df['Location'].value_counts().head(10).reset_index()
    top_locations.columns = ['Location', 'Count']
    
    return html.Div([
        html.H1('Analytics', style={'margin': '0 0 20px 0'}),
        html.P('Advanced analytics and insights about the hospital data.'),
        
        # Analytics charts
        html.Div([
            # Average Beds by Size
            html.Div([
                html.H3('Average Beds by Size Category', style={'padding': '15px', 'margin': '0', 
                                                              'borderBottom': '1px solid #ddd'}),
                dcc.Graph(
                    figure=px.bar(
                        beds_by_size,
                        x='Size Category',
                        y='Estimated Beds',
                        color='Size Category',
                        labels={'Estimated Beds': 'Average Number of Beds'},
                        color_discrete_map={
                            'Small': '#1cc88a',
                            'Medium': '#4e73df',
                            'Large': '#e74a3b',
                            'N/A': '#f6c23e'
                        }
                    ).update_layout(
                        margin=dict(l=40, r=40, t=40, b=40),
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        height=400
                    )
                )
            ], style={'backgroundColor': 'white', 'borderRadius': '5px', 
                      'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
            
            # Top Locations
            html.Div([
                html.H3('Top 10 Hospital Locations', style={'padding': '15px', 'margin': '0', 
                                                          'borderBottom': '1px solid #ddd'}),
                dcc.Graph(
                    figure=px.bar(
                        top_locations,
                        x='Count',
                        y='Location',
                        orientation='h',
                        color_discrete_sequence=['#4e73df']
                    ).update_layout(
                        margin=dict(l=40, r=40, t=40, b=40),
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        height=400,
                        yaxis={'categoryorder': 'total ascending'}
                    )
                )
            ], style={'backgroundColor': 'white', 'borderRadius': '5px', 
                      'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ])
    ])

# Table page content
def render_table_page():
    return html.Div([
        html.H1('Table View', style={'margin': '0 0 20px 0'}),
        html.P('Complete dataset in tabular format with filtering and sorting capabilities.'),
        
        # Full data table
        html.Div([
            dash_table.DataTable(
                id='data-table',
                columns=[{'name': col, 'id': col} for col in df.columns],
                data=df.to_dict('records'),
                page_size=20,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '100px',
                    'maxWidth': '300px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis'
                },
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'borderBottom': '1px solid #ddd'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8f9fa'
                    }
                ],
                filter_action='native',
                sort_action='native',
                export_format='csv'
            )
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '5px', 
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    ])

# Callback to enable/disable dropdowns based on filter type
@app.callback(
    [Output('size-dropdown', 'disabled'),
     Output('specialty-dropdown', 'disabled')],
    [Input('filter-type', 'value')]
)
def update_dropdown_state(filter_type):
    if filter_type == 'size':
        return False, True
    elif filter_type == 'specialty':
        return True, False
    else:  # 'all'
        return True, True

# Callback to update map based on filters
@app.callback(
    Output('map-chart', 'figure'),
    [Input('filter-type', 'value'),
     Input('size-dropdown', 'value'),
     Input('specialty-dropdown', 'value')]
)
def update_map(filter_type, selected_size, selected_specialty):
    filtered_df = df.copy()
    
    if filter_type == 'size' and selected_size:
        filtered_df = filtered_df[filtered_df['Size Category'] == selected_size]
    elif filter_type == 'specialty' and selected_specialty:
        filtered_df = filtered_df[filtered_df['Primary Specialty'] == selected_specialty]
    
    fig = px.scatter_map(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        color='Size Category',
        hover_name='Hospital/Organization',
        hover_data=['Location', 'Estimated Beds', 'Primary Specialty'],
        color_discrete_map={
            'Small': '#1cc88a',
            'Medium': '#4e73df',
            'Large': '#e74a3b',
            'N/A': '#f6c23e'
        },
        zoom=3,
        height=600
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

# Add Font Awesome for icons
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
