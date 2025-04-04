import streamlit as st
import pandas as pd
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pickle as cp
import base64

PUBTATOR_PICKLE = "output/pubtator_pubs.pkl"


def display_nd_data(nd_df):
    """Display ND proteins information"""
    st.header("Proteins with ND Status")
    
    # Show total number of ND proteins
    st.metric("Total ND Proteins", len(nd_df))
    
    nd_df['year'] = nd_df['year'].astype(str)
    # Display the dataframe
    st.dataframe(nd_df, use_container_width=True)
    
    # Create visualization for ND annotations
    chart = alt.Chart(nd_df).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('count()', title='Number of Proteins'),
        color=alt.Color('aspect:N', title='Aspect')
    ).properties(
        title='ND Annotations by Year and Aspect'
    )
    st.altair_chart(chart, use_container_width=True)


def create_checkbox_filter(df, column_name, default_state=True, num_columns=3):
    """
    Create checkbox filters for unique values in a specified column.
    Parameters:
    - df: pandas DataFrame
    - column_name: str, name of the column to create filters for
    - default_state: bool, default state of checkboxes
    - num_columns: int, number of columns to display checkboxes in
    
    Returns:
    - list of selected values
    - dictionary of checkbox states
    """
    # Get unique values from the column
    unique_values = sorted(df[column_name].unique())
    
    # Create columns for layout
    cols = st.columns(num_columns)
    
    # Create a dictionary to store checkbox states
    selected_values = {}
    
    # Distribute checkboxes across columns
    for idx, value in enumerate(unique_values):
        col_idx = idx % num_columns
        with cols[col_idx]:
            selected_values[value] = st.checkbox(
                str(value),
                value=default_state,
                key=f"{column_name}_{value}"
            )
    
    # Get selected values
    selected = [value for value, selected in selected_values.items() if selected]
    
    return selected, selected_values


def create_aggrid_hover_table(df, unreviewed_dict):
    """
    Create an interactive AgGrid table with hover feature, search functionality,
    and color-coded rows based on protein existence levels
    """
    # First get the set of valid uniprot_ids from the filtered df
    valid_uniprot_ids = set(df['uniprot_id'].values)
    
    # Helper function to safely extract values, only from valid proteins
    def safe_get_values(dict_data, valid_ids):
        all_scores = []
        all_years = []
        
        for key, value in dict_data.items():
            if key in valid_ids and isinstance(value, pd.DataFrame):
                all_scores.extend(value['score'].astype(float).tolist())
                all_years.extend(value['year'].astype(str).tolist())
                
        return all_scores, all_years

    # Create column layout for filters
    col1, col2 = st.columns(2)
    
    # Get all scores and years safely, only from valid proteins
    all_scores, all_years = safe_get_values(unreviewed_dict, valid_uniprot_ids)
    
    if not all_scores or not all_years:
        st.error("No valid data found to create filters")
        return None

    # # Add score filter input boxes
    # with col1:
    #     st.write("Filter publications by PubTator relevance score range")
    #     score_col1, score_col2 = st.columns(2)
        
    #     min_score = min(float(s) for s in all_scores)
    #     max_score = max(float(s) for s in all_scores)
        
    #     with score_col1:
    #         min_score_input = st.number_input(
    #             "Minimum score",
    #             min_value=float(min_score),
    #             max_value=float(max_score),
    #             value=float(min_score),
    #             step=0.1
    #         )
        
    #     with score_col2:
    #         max_score_input = st.number_input(
    #             "Maximum score",
    #             min_value=float(min_score),
    #             max_value=float(max_score),
    #             value=float(max_score),
    #             step=0.1
    #         )
    
    # Add fraction_mentions filter input boxes
    with col1:
        st.write("Filter publications by fraction of gene mentions")
        fraction_col1, fraction_col2 = st.columns(2)
        
        # Calculate min/max fraction_mentions
        all_fractions = []
        for key, value in unreviewed_dict.items():
            if key in valid_uniprot_ids and isinstance(value, pd.DataFrame):
                all_fractions.extend(value['fraction_mentions'].astype(float).tolist())
        
        min_fraction = 0.0
        max_fraction = 1.0
        if all_fractions:
            min_fraction = max(0.0, min(float(f) for f in all_fractions))
            max_fraction = min(1.0, max(float(f) for f in all_fractions))
        
        with fraction_col1:
            min_fraction_input = st.number_input(
                "Minimum fraction",
                min_value=0.0,
                max_value=1.0,
                value=min_fraction,
                step=0.01
            )
        
        with fraction_col2:
            max_fraction_input = st.number_input(
                "Maximum fraction",
                min_value=0.0,
                max_value=1.0,
                value=max_fraction,
                step=0.01
            )
        
    # Add year filter input boxes
    with col2:
        st.write("Filter publications by publication year range")
        year_col1, year_col2 = st.columns(2)
        
        min_year = int(min(int(y) for y in all_years))
        max_year = int(max(int(y) for y in all_years))
        
        with year_col1:
            min_year_input = st.number_input(
                "Minimum year",
                min_value=min_year,
                max_value=max_year,
                value=min_year,
                step=1
            )
        
        with year_col2:
            max_year_input = st.number_input(
                "Maximum year",
                min_value=min_year,
                max_value=max_year,
                value=max_year,
                step=1
            )

        # Add search box
    
    col1, col2 = st.columns(2)
    with col1:
        search_query = st.text_input(
        "Search proteins (multiple terms separated by comma)",
        help="Enter search terms separated by commas. The search is case-insensitive and matches partial text."
    )
    with col2:
        # Add filter for last reviewed publication year
        st.write("Filter proteins by last reviewed publication year")
        last_reviewed_col1, last_reviewed_col2 = st.columns(2)
        with last_reviewed_col1:
            
            min_last_reviewed = int(df['last_reviewed_pubyear'].min())
            max_last_reviewed = int(df['last_reviewed_pubyear'].max())
            
            min_last_reviewed_input = st.number_input(
                "Minimum last reviewed year",
                min_value=min_last_reviewed,
                max_value=max_last_reviewed,
                value=min_last_reviewed,
                step=1
            )
        with last_reviewed_col2:
            max_last_reviewed_input = st.number_input(
                "Maximum last reviewed year",
                min_value=min_last_reviewed,
                max_value=max_last_reviewed,
                value=max_last_reviewed,
                step=1
            )
    
    # Filter the main DataFrame based on last reviewed publication year
    df = df.copy()

    # Handle potential NaN values that might result from the conversion
    df = df[
        (df['last_reviewed_pubyear'].notna()) & 
        (df['last_reviewed_pubyear'] >= min_last_reviewed_input) & 
        (df['last_reviewed_pubyear'] <= max_last_reviewed_input)
    ]
    valid_uniprot_ids = set(df['uniprot_id'].values) # reset valid_uniprot_ids after filtering
    # Filter unreviewed_dict based on both fraction and year cutoffs
    filtered_unreviewed_dict = {}
    
    for uniprot_id in valid_uniprot_ids:
        if uniprot_id in unreviewed_dict:
            data = unreviewed_dict[uniprot_id]
            if isinstance(data, pd.DataFrame):
                try:
                    filtered_data = data[
                        (data['fraction_mentions'].astype(float) >= min_fraction_input) & 
                        (data['fraction_mentions'].astype(float) <= max_fraction_input) & 
                        (data['year'].astype(int) >= min_year_input) & 
                        (data['year'].astype(int) <= max_year_input)
                    ]
                    filtered_unreviewed_dict[uniprot_id] = filtered_data
                except Exception as e:
                    st.error(f"Error processing protein {uniprot_id}: {str(e)}")
                    continue

    # Update num_unreviewed_publications in the main DataFrame
    df = df.copy()
    df['num_unreviewed_publications'] = df['uniprot_id'].apply(
        lambda x: len(filtered_unreviewed_dict.get(x, pd.DataFrame()))
    )

    # Define color mapping for protein existence levels
    color_map = {
        'Evidence at protein level': '#2ecc71',
        'Evidence at transcript level': '#3498db',
        'Inferred from homology': '#e74c3c',
        'Predicted': '#f1c40f',
        'Uncertain': '#95a5a6'
    }

    # Create row styling function
    row_style = JsCode(f"""
    function(params) {{
        const colorMap = {str(color_map)};
        if (params.data) {{
            const level = params.data.protein_existence;
            const color = colorMap[level];
            if (color) {{
                return {{
                    'background-color': color + '66'  // Adding 66 for 40% opacity
                }};
            }}
        }}
        return null;
    }}
    """)

    cell_renderer = JsCode("""
    class PublicationsRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.classList.add('publications-cell');
            this.uniprot_id = params.data ? params.data.uniprot_id : null;
            
            const context = params.context || {};
            const unreviewedDict = context.unreviewedDict || {};
            this.unreviewedData = this.uniprot_id ? (unreviewedDict[String(this.uniprot_id)] || []) : [];
            
            this.render();
            
            // Add click handler to the cell
            this.eGui.addEventListener('click', this.showModal.bind(this));
        }
        
        getGui() {
            return this.eGui;
        }
        
        refresh(params) {
            this.params = params;
            return true;
        }
        
        render() {
            if (!this.unreviewedData || this.unreviewedData.length === 0) {
                this.eGui.innerHTML = `<span>0</span>`;
                return;
            }
            
            // Simple display showing count and button
            this.eGui.innerHTML = `
                <div class="cell-container">
                    <div class="cell-header">
                        <span>${this.unreviewedData.length}</span>
                        <button class="view-btn" title="Click to view publications">View</button>
                    </div>
                </div>
            `;
        }
        
        showModal(event) {
            // Prevent default grid behavior
            event.stopPropagation();
            
            // Skip if no data
            if (!this.unreviewedData || this.unreviewedData.length === 0) {
                return;
            }
            
            // Check if modal already exists, remove it if so
            let existingModal = document.getElementById('publications-modal');
            if (existingModal) {
                document.body.removeChild(existingModal);
            }
            
            // Create modal container
            const modal = document.createElement('div');
            modal.id = 'publications-modal';
            modal.classList.add('publications-modal');
            
            // Get protein details for the modal header
            const proteinName = this.params.data.gene_name || 'Unknown';
            const ncbiId = this.params.data.ncbi_gene || 'Unknown';
            const uniprotId = this.uniprot_id || 'Unknown';
            const geneDescription = this.params.data.description || this.params.data.gene_description || 'No description available';
            const geneAliases = this.params.data.aliases || this.params.data.gene_aliases || 'None';
            
            // Create modal content
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>Publications for ${proteinName} (UniProt: ${uniprotId}, NCBI Gene: ${ncbiId})</h2>
                        <h3 class="modal-subheading">Description: ${geneDescription}. Aliases: ${geneAliases}</h3>
                        <span class="close-btn">&times;</span>
                    </div>
                    <div class="modal-body">
                        <div class="filters-section">
                            <input type="text" class="search-input" placeholder="Filter by text in title or PMID..." />
                            <div class="sort-controls">
                                <label>Sort by: 
                                    <select class="sort-select">
                                        <option value="year_desc">Year (newest first)</option>
                                        <option value="year_asc">Year (oldest first)</option>
                                        <option value="fraction_desc">Fraction (highest first)</option>
                                    </select>
                                </label>
                            </div>
                        </div>
                        <div class="publications-table-container">
                            <table class="publications-table">
                                <thead>
                                    <tr>
                                        <th>PMID</th>
                                        <th>Year</th>
                                        <th>In Title</th>
                                        <th>Fraction</th>
                                        <th>Total Genes</th>
                                        <th>Journal</th>
                                        <th>Full Text</th>
                                        <th class="title-column">Title</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${this.unreviewedData.map(pub => `
                                        <tr>
                                            <td><a href="https://www.ncbi.nlm.nih.gov/research/pubtator3/publication/${pub.pmid || ''}" target="_blank">${pub.pmid || ''}</a></td>
                                            <td>${pub.year || ''}</td>
                                            <td>${pub.in_title || 'false'}</td>
                                            <td>${pub.fraction_mentions ? Number(pub.fraction_mentions).toFixed(2) : ''}</td>
                                            <td>${pub.total_genes || ''}</td>
                                            <td>${pub.journal || ''}</td>
                                            <td>${pub.full_text || 'false'}</td>
                                            <td class="title-column">${pub.title || ''}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="close-modal-btn">Close</button>
                    </div>
                </div>
            `;
            
            // Add modal to document
            document.body.appendChild(modal);
            
            // Show modal with animation
            setTimeout(() => {
                modal.classList.add('show');
            }, 10);
            
            // Close button functionality
            const closeBtn = modal.querySelector('.close-btn');
            const closeModalBtn = modal.querySelector('.close-modal-btn');
            const closeModal = () => {
                modal.classList.remove('show');
                setTimeout(() => {
                    document.body.removeChild(modal);
                }, 300);
            };
            
            closeBtn.addEventListener('click', closeModal);
            closeModalBtn.addEventListener('click', closeModal);
            
            // Close when clicking outside the modal content
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    closeModal();
                }
            });
            
            // Add search functionality
            const searchInput = modal.querySelector('.search-input');
            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                const rows = modal.querySelectorAll('.publications-table tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            });
            
            // Add sorting functionality
            const sortSelect = modal.querySelector('.sort-select');
            sortSelect.addEventListener('change', (e) => {
                const sortValue = e.target.value;
                const tbody = modal.querySelector('.publications-table tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                rows.sort((a, b) => {
                    if (sortValue === 'year_desc') {
                        return parseInt(b.children[1].textContent || '0') - parseInt(a.children[1].textContent || '0');
                    } else if (sortValue === 'year_asc') {
                        return parseInt(a.children[1].textContent || '0') - parseInt(b.children[1].textContent || '0');
                    } else if (sortValue === 'score_desc') {
                        return parseFloat(b.children[2].textContent || '0') - parseFloat(a.children[2].textContent || '0');
                    } else if (sortValue === 'fraction_desc') {
                        return parseFloat(b.children[4].textContent || '0') - parseFloat(a.children[4].textContent || '0');
                    }
                    return 0;
                });
                
                // Remove existing rows
                while (tbody.firstChild) {
                    tbody.removeChild(tbody.firstChild);
                }
                
                // Add sorted rows
                rows.forEach(row => tbody.appendChild(row));
            });
        }
    }
    """)
    
    # Apply search filter if search terms exist
    if search_query:
        search_terms = [term.strip().lower() for term in search_query.split(',')]
        mask = df.apply(
            lambda row: any(
                any(term in str(value).lower() for value in row)
                for term in search_terms
            ),
            axis=1
        )
        df = df[mask]
    
    
    # Convert filtered_unreviewed_dict DataFrames to lists of dicts for JS
    js_unreviewed_dict = {}
    for uniprot_id, df_pub in filtered_unreviewed_dict.items():
        if isinstance(df_pub, pd.DataFrame) and not df_pub.empty:
            # Convert to list of dictionaries, ensuring values are JSON serializable
            records = []
            for _, row in df_pub.iterrows():
                record = {}
                for col in df_pub.columns:
                    value = row[col]
                    # Convert non-serializable values to strings
                    if pd.isna(value):
                        record[col] = None
                    elif isinstance(value, (int, float, bool, str)):
                        record[col] = value
                    else:
                        record[col] = str(value)
                records.append(record)
            js_unreviewed_dict[str(uniprot_id)] = records
        else:
            # Ensure we always have at least an empty array for each uniprot_id
            js_unreviewed_dict[str(uniprot_id)] = []
            
    # Build grid options
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # Configure columns to prevent width collapse
    gb.configure_default_column(
        tooltipComponent='CustomTooltip',
        minWidth=100,
        flex=1
    )
    
    # Hide the protein_existence column
    gb.configure_column(
        'protein_existence',
        hide=True
    )
    gb.configure_column(
        'reviewed_publications',
        hide=True
    )
    gb.configure_column(
        'num_total_PubTator',
        hide=True
    )
    gb.configure_column(
        'gene_aliases',
        hide=True
    )

    # Configure the num_unreviewed_publications column specially
    gb.configure_column(
        'num_unreviewed_publications',
        headerName='Unreviewed Publications',
        headerTooltip="Click on cell to view publication details",
        tooltipField='num_unreviewed_publications',
        width=150,
        minWidth=120,
        cellRenderer="PublicationsRenderer",
        # autoHeight=True,
        cellStyle={"cursor": "pointer"}
    )
    
    # Update the tooltip to match the modal approach (around line 640-680)
    custom_tooltip = JsCode("""
    class CustomTooltip {
        init(params) {
            this.eGui = document.createElement('div');
            this.eGui.classList.add('custom-tooltip');
            
            if (params.colDef.field === 'num_unreviewed_publications') {
                const uniprot_id = params.data ? params.data.uniprot_id : null;
                if (!uniprot_id) {
                    this.eGui.innerHTML = 'No data available';
                    return;
                }
                
                const unreviewedData = params.context && params.context.unreviewedDict ? 
                    params.context.unreviewedDict[String(uniprot_id)] || [] : [];
                
                if (!unreviewedData || unreviewedData.length === 0) {
                    this.eGui.innerHTML = 'No publications found';
                } else {
                    const previewCount = Math.min(unreviewedData.length, 5);
                    const previewData = unreviewedData.slice(0, previewCount);
                    
                    this.eGui.innerHTML = `
                        <div>
                            <p style="margin-bottom: 8px; font-weight: bold;">
                                ${unreviewedData.length} publication(s) - Preview:
                            </p>
                            <table style="border-collapse: collapse; width: 100%; margin-bottom: 8px;">
                                <tr style="background-color: #f0f0f0;">
                                    <th style="padding: 4px; border: 1px solid #ddd;">PMID</th>
                                    <th style="padding: 4px; border: 1px solid #ddd;">Year</th>
                                    <th style="padding: 4px; border: 1px solid #ddd;">Score</th>
                                    <th style="padding: 4px; border: 1px solid #ddd;">Fraction</th>
                                </tr>
                                ${previewData.map(pub => `
                                    <tr>
                                        <td style="padding: 4px; border: 1px solid #ddd;">${pub.pmid || ''}</td>
                                        <td style="padding: 4px; border: 1px solid #ddd;">${pub.year || ''}</td>
                                        <td style="padding: 4px; border: 1px solid #ddd;">${pub.score ? Number(pub.score).toFixed(2) : ''}</td>
                                        <td style="padding: 4px; border: 1px solid #ddd;">${pub.fraction_mentions ? Number(pub.fraction_mentions).toFixed(2) : ''}</td>
                                    </tr>
                                `).join('')}
                            </table>
                            <p style="color: #666; font-size: 0.9em; margin: 0;">
                                Click to view all publications in fullscreen modal
                            </p>
                        </div>
                    `;
                }
            } else {
                this.eGui.innerHTML = params.value || '';
            }
        }
        
        getGui() {
            return this.eGui;
        }
    }
    """)
    
    # Configure grid options with updated components and defensive programming
    gb.configure_grid_options(
        tooltipShowDelay=0,
        tooltipHideDelay=2000,
        context={'unreviewedDict': js_unreviewed_dict},
        tooltipComponent='CustomTooltip',
        components={
            'CustomTooltip': custom_tooltip,
            'PublicationsRenderer': cell_renderer
        },
        getRowStyle=row_style,
        suppressClickEdit=True,
        # domLayout='autoHeight',
        # getRowHeight=JsCode("""
        #     function(params) {
                
        #         return 42;
        #     }
        # """)
        pagination=True,
        paginationPageSize=50,  # Show 50 rows per page
        paginationAutoPageSize=False,
        rowHeight=42
    )

    # Get the grid options from the builder
    grid_options = gb.build()
    
    # Define custom CSS for styling
    custom_css = {
        ".ag-row-hover": {"background-color": "#f0f0f0 !important"},
        ".ag-header-cell-label": {"font-weight": "bold"},
        ".custom-tooltip": {
            "position": "absolute",
            "background-color": "white",
            "border": "1px solid #ccc",
            "padding": "10px",
            "font-size": "12px",
            "font-family": "Arial, sans-serif",
            "max-height": "400px",
            "max-width": "800px",
            "overflow-y": "auto",
            "box-shadow": "3px 3px 5px rgba(0,0,0,0.2)",
            "z-index": "9999",
            "cursor": "default"
        },
        ".publications-cell": {
            "width": "100%",
            "cursor": "pointer"
        },
        ".cell-container": {
            "width": "100%",
            "position": "relative"
        },
        ".cell-header": {
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "center",
            "padding": "4px",
            "width": "100%"
        },
        ".toggle-btn": {
            "background-color": "#4CAF50",
            "border": "none",
            "color": "white",
            "cursor": "pointer",
            "font-size": "14px",
            "padding": "2px 6px",
            "border-radius": "3px",
            "margin-left": "10px"
        },
        ".details-container": {
            "background-color": "#f9f9f9",
            "border": "1px solid #ddd",
            "border-radius": "4px",
            "padding": "10px",
            "margin-top": "4px",
            "overflow": "hidden",
            "width": "100%"
        },
        ".publications-table-container": {
            "max-height": "300px",
            "overflow-y": "auto",
            "margin-top": "8px"
        },
        ".publications-table": {
            "width": "100%",
            "border-collapse": "collapse",
            "font-size": "12px"
        },
        ".publications-table th": {
            "background-color": "#f0f0f0",
            "padding": "6px",
            "text-align": "left",
            "border": "1px solid #ddd",
            "position": "sticky",
            "top": "0",
            "z-index": "1"
        },
        ".publications-table td": {
            "padding": "4px",
            "border": "1px solid #ddd",
            "max-width": "150px",
            "white-space": "nowrap",
            "overflow": "hidden",
            "text-overflow": "ellipsis"
        }
    }
    
    custom_css.update({
        # Keep your existing styles and add these new ones:
        ".view-btn": {
            "background-color": "#4CAF50",
            "border": "none",
            "color": "white", 
            "cursor": "pointer",
            "font-size": "13px",
            "padding": "2px 8px",
            "border-radius": "3px",
            "margin-left": "10px"
        },
        ".publications-modal": {
            "display": "flex",
            "position": "fixed",
            "z-index": "1000",
            "left": "0",
            "top": "0",
            "width": "100%",
            "height": "100%",
            "background-color": "rgba(0,0,0,0.5)",
            "opacity": "0",
            "transition": "opacity 0.3s ease",
            "justify-content": "center",
            "align-items": "center"
        },
        ".publications-modal.show": {
            "opacity": "1"
        },
        ".modal-content": {
            "background-color": "white",
            "border-radius": "8px",
            "width": "90%",
            "max-width": "1200px",
            "max-height": "90%",
            "display": "flex",
            "flex-direction": "column",
            "box-shadow": "0 4px 20px rgba(0,0,0,0.2)",
            "transform": "translateY(-20px)",
            "transition": "transform 0.3s ease",
            "overflow": "hidden"
        },
        ".publications-modal.show .modal-content": {
            "transform": "translateY(0)"
        },
        ".modal-header": {
            "padding": "15px 20px",
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "center",
            "border-bottom": "1px solid #eee",
            "background-color": "#f8f9fa"
        },
        ".modal-subheading": {
            "margin-top": "5px",
            "margin-bottom": "10px",
            "font-size": "14px",
            "color": "#666",
            "font-weight": "normal"
        },
        ".close-btn": {
            "font-size": "28px",
            "font-weight": "bold",
            "cursor": "pointer"
        },
        ".modal-body": {
            "padding": "20px",
            "overflow-y": "auto",
            "flex": "1"
        },
        ".modal-footer": {
            "padding": "15px",
            "text-align": "right",
            "border-top": "1px solid #eee"
        },
        ".close-modal-btn": {
            "background-color": "#6c757d",
            "color": "white",
            "border": "none",
            "padding": "8px 16px",
            "border-radius": "4px",
            "cursor": "pointer"
        },
        ".filters-section": {
            "display": "flex",
            "justify-content": "space-between",
            "margin-bottom": "15px",
            "flex-wrap": "wrap",
            "gap": "10px"
        },
        ".search-input": {
            "padding": "8px",
            "border": "1px solid #ddd",
            "border-radius": "4px",
            "width": "300px",
            "max-width": "100%"
        },
        ".sort-controls": {
            "display": "flex",
            "align-items": "center"
        },
        ".sort-select": {
            "padding": "8px",
            "border": "1px solid #ddd",
            "border-radius": "4px",
            "margin-left": "5px"
        },
        ".title-column": {
            "min-width": "300px",
            "white-space": "normal !important"
        },
        ".publications-table-container": {
            "max-height": "calc(90vh - 200px)",
            "overflow-y": "auto",
        }
    })
    
    try:
        # Display summary metrics in columns
        col1, col2 = st.columns(2)
        
        # Display the grid
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            allow_unsafe_jscode=True,
            custom_css=custom_css,
            height=600,  # Increase height to better accommodate expanded rows
            fit_columns_on_grid_load=True,
            theme="streamlit",
            update_mode='value_changed',
            data_return_mode='filtered_and_sorted',
            reload_data=True,  # Force reload data
            enable_enterprise_modules=False,
            key=f"grid_{len(df)}",  # Dynamic key based on data size
        )
        
        # Display summary statistics
        total_filtered_pubs = sum(len(pubs) for pubs in filtered_unreviewed_dict.values())
        proteins_with_pubs = sum(1 for pubs in filtered_unreviewed_dict.values() if len(pubs) > 0)
        
        with col1:
            st.metric("Total publications meeting criteria", total_filtered_pubs)
        with col2:
            st.metric("Proteins with matching publications", proteins_with_pubs)
        
        return grid_response
        
    except Exception as e:
        st.error(f"Error displaying grid: {str(e)}")
        st.write("Falling back to standard dataframe display")
        st.dataframe(df)
        return None
        # TODO: doesn't work with dark mode


def create_download_link(uniprot_id, filtered_unreviewed_dict):
    """Create a download link for a specific protein's publications data"""
    if uniprot_id in filtered_unreviewed_dict:
        df = filtered_unreviewed_dict[uniprot_id]
        csv = df.to_csv(index=False,sep="\t")
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'data:file/tsv;base64,{b64}'
        return href
    return None

    
def display_non_nd_data(non_nd_df, unreviewed_dict):
    """Display non-ND proteins information"""
    st.header("Proteins without GO Annotations")
    
    # Show total number of non-ND proteins
    st.metric("Total Proteins", len(non_nd_df))
    
    # Format last reviewed publication year
    non_nd_df['last_reviewed_pubyear'] = non_nd_df['last_reviewed_pubyear'].apply(
lambda x: (int(x)) if not pd.isnull(x) else x
)
    
    # Display protein evidence level distribution
    evidence_dist = non_nd_df['protein_existence'].value_counts()
    evidence_chart = alt.Chart(
        evidence_dist.reset_index().rename(
            columns={'index': 'Protein Existence', 'protein_existence': 'Count'}
        )
    ).mark_bar().encode(
        x=alt.X('Protein Existence:N', sort='x'),
        y='Count:Q',
        color=alt.Color('Protein Existence:N', legend=None)
    ).properties(
        title='Barplot of Protein Existence',
        height=500
    )
    st.altair_chart(evidence_chart, use_container_width=True)
    
    # Create filters for protein existence levels
    selected_levels, selected_existence = create_checkbox_filter(
        non_nd_df,
        'protein_existence',
        default_state=True,
        num_columns=2
    )
    
    filtered_df = non_nd_df[non_nd_df['protein_existence'].isin(selected_levels)]
    st.metric("Proteins with Selected Existence", len(filtered_df)) 
    
    # Display protein information with interactive grid
    create_aggrid_hover_table(filtered_df, unreviewed_dict)
    
    
def main():
    st.title("Protein Annotation Analysis")
    try:
        # Load your pre-processed dataframes here
        # nd_data = pd.read_csv('ND_proteins_112724.tsv',sep="\t",header=0)  
        # non_nd_info_df = pd.read_csv('non_ND_proteins_112724.tsv',sep="\t",header=0)  
        (non_nd_df, unreviewed_dict) = cp.load(open(PUBTATOR_PICKLE, "rb"))
        new_unreviewed_dict = {}
        # Remove unreviewed publications before last_reviewed_pubyear
        for uniprot_id, data in unreviewed_dict.items():
            last_reviewed_year = non_nd_df.loc[non_nd_df['uniprot_id'] == uniprot_id, 'last_reviewed_pubyear'].iloc[0]
            if pd.isna(last_reviewed_year):
                last_reviewed_year = 0
            data = data[data['year'].astype(int) > last_reviewed_year]
            new_unreviewed_dict[uniprot_id] = data
        # Create tabs
        tab1, tab2 = st.tabs(["Proteins with No Annotations", "Other Proteins"])
        
        # Display non-ND proteins in the first tab        
        with tab1:
            display_non_nd_data(non_nd_df, new_unreviewed_dict)
            
            # Add download button for non-ND data
            csv_non_nd = non_nd_df.to_csv(index=False)
            st.download_button(
                label="Download Data",
                data=csv_non_nd,
                file_name="non_nd_proteins.csv",
                mime="text/csv"
            )

        # Placeholder for future ND proteins tab functionality
        # with tab2:
        #     display_nd_data(nd_data)
            
        #     csv_nd = nd_data.to_csv(index=False)
        #     st.download_button(
        #         label="Download ND Data",
        #         data=csv_nd,
        #         file_name="nd_proteins.csv",
        #         mime="text/csv"
        #     )
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()


if __name__ == "__main__":
    st.set_page_config(
        page_title="IgnoroMeNot: Prioritizing Proteins for Literature Curation",
        page_icon="🧬",
        layout="wide"
    )
    main()