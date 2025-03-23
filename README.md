# Hospital Dashboard - Complete User Guide

This guide provides comprehensive instructions for deploying and using the Hospital Dashboard application created with Plotly Dash.

## Features

The dashboard includes the following features:

1. **Sidebar Navigation** with five sections:
   - Summary - Overview with key metrics and charts
   - Companies - Card-based view of hospitals with search functionality
   - Map View - Interactive map with filtering capabilities
   - Analytics - Additional charts and insights
   - Table View - Complete dataset in tabular format

2. **Companies View**:
   - Card-based layout showing hospital information
   - Search functionality to filter hospitals
   - Visual indicators for hospital size and location
   - Hospital descriptions and founding information

3. **Interactive Filtering** on the Map View:
   - Filter by hospital size (Small, Medium, Large)
   - Filter by specialty focus

4. **Data Tables** with advanced features:
   - Sorting capabilities
   - Filtering capabilities
   - Pagination
   - CSV export (in Table View)

5. **Analytics** with insights:
   - Average beds by size category
   - Top hospital locations

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

## Required Packages

The dashboard requires the following Python packages:
```
pandas
openpyxl
plotly
dash
```

## Installation Steps

1. Install the required packages:
   ```
   pip install pandas openpyxl plotly dash
   ```

2. Place your data file (`Complete_Hospital_Locations_and_Sizes.xlsx`) and logo file (`_eo_scale_yourself.png`) in the same directory as the script or update the file paths in the code.

3. Run the dashboard:
   ```
   python hospital_dashboard_with_cards.py
   ```

4. Access the dashboard in your web browser at:
   ```
   http://localhost:8050
   ```

## Using the Dashboard

### Navigation

Use the sidebar on the left to navigate between different sections of the dashboard:

- **Summary**: Overview with key metrics and charts
- **Companies**: Card-based view of hospitals with search functionality
- **Map View**: Interactive map with filtering capabilities
- **Analytics**: Additional charts and insights
- **Table View**: Complete dataset in tabular format

### Companies View

The Companies section displays hospitals in a card-based layout:

1. Use the search bar at the top to filter hospitals by name, location, or specialty
2. Each card shows:
   - Hospital initial in a circle
   - Hospital name
   - Size category badge (color-coded)
   - Location badge
   - Brief description
   - Founding year
   - Visit button

The search functionality updates the displayed cards in real-time as you type.

### Filtering the Map

1. Navigate to the Map View section
2. Select a filter type:
   - "All Hospitals" - Shows all hospitals on the map
   - "By Size" - Enables the size dropdown to filter by hospital size
   - "By Specialty" - Enables the specialty dropdown to filter by hospital specialty
3. Use the appropriate dropdown to select a specific size or specialty
4. The map will update in real-time to show only the filtered hospitals

### Using the Data Tables

The Table View section includes an interactive data table with the following features:

- Click on column headers to sort the data
- Use the filter row to filter data by specific values
- Navigate between pages using the pagination controls
- Export the data to CSV format using the export button

### Analytics

The Analytics section provides additional insights:

- Average Beds by Size Category - Bar chart showing the average number of beds for each hospital size
- Top 10 Hospital Locations - Horizontal bar chart showing the locations with the most hospitals

## Customization Options

### Modifying the Color Scheme

You can customize the color scheme by modifying the color variables in the code:

- Primary color: `#4e73df` (blue)
- Success color: `#1cc88a` (green)
- Info color: `#36b9cc` (light blue)
- Warning color: `#f6c23e` (yellow)
- Danger color: `#e74a3b` (red)
- Secondary color: `#6c757d` (gray)

### Adding More Cards to the Companies View

To display more hospital cards on the Companies page, modify the sample size in the `filter_companies` callback function:

```python
def filter_companies(search_term):
    if not search_term:
        return df.sample(min(12, len(df))).to_dict('records')  # Change 8 to 12 or any desired number
    
    # Rest of the function...
```

### Changing the Map Style

To change the map style, modify the `mapbox_style` parameter in the `update_map` callback function:

```python
fig.update_layout(
    mapbox_style="light",  # Options: "open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner", "stamen-watercolor"
    margin=dict(l=0, r=0, t=0, b=0)
)
```

## Production Deployment Options

For production deployment, consider the following options:

1. **Heroku**: Deploy using the Procfile included in the package.
   - Create a requirements.txt file with the dependencies
   - Create a Procfile with: `web: gunicorn app:server`
   - Deploy to Heroku using their CLI or GitHub integration

2. **AWS Elastic Beanstalk**: Deploy as a Python application.
   - Create a requirements.txt file
   - Configure the application to run on port 8050
   - Deploy using the AWS EB CLI

3. **Docker**: Containerize the application.
   - Use the included Dockerfile
   - Build and run the container

## Troubleshooting

### Common Issues

1. **Map not displaying**: Ensure you have internet connectivity as the map uses OpenStreetMap tiles.

2. **Data not loading**: Check that the Excel file path is correct and the file format is as expected.

3. **Search not working**: Verify that the column names in your data match those used in the search function.

### Performance Optimization

For large datasets, consider:

1. Pre-processing data before loading into the dashboard
2. Implementing data caching
3. Using dcc.Store components to store processed data
4. Limiting the number of displayed items in card views and tables

## Support

For any questions or issues, please contact your dashboard provider.
