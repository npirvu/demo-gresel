---
# create lunr store for search page
---
{% if site.data.theme.search-child-objects == true %}
{%- assign items = site.data[site.metadata] | where_exp: 'item','item.objectid' -%}
{% else %}
{%- assign items = site.data[site.metadata] | where_exp: 'item','item.objectid and item.parentid == nil' -%}
{% endif %}
{%- assign fields = site.data.config-search -%}
var store = [ 
{%- for item in items -%} 
{  
{% for f in fields %}{% if item[f.field] %}{{ f.field | jsonify }}: {{ item[f.field] | normalize_whitespace | replace: '""','"' | jsonify }},{% endif %}{% endfor %}
{%- if item.object_transcript -%}"object_transcript": {{ item.object_transcript | jsonify }},{%- endif -%}
"transcript_text": "",
"id": {% if item.parentid %}{{ item.parentid | append: '.html#' | append: item.objectid | jsonify }}{% else %}{{item.objectid | append: '.html' | jsonify }}{% endif %}

}{%- unless forloop.last -%},{%- endunless -%}
{%- endfor -%}
];

// Load transcript text from TXT files
(async function loadTranscriptText() {
    const loadingPromises = store.map(async (item) => {
        try {
            if (!item.object_transcript) {
                return;
            }
            
            const response = await fetch(`{{ '/' | relative_url }}${item.object_transcript}`);
            
            if (!response.ok) {
                return;
            }
            
            // Read the text content directly
            const transcriptText = await response.text();
            
            // Store the transcript text
            item.transcript_text = transcriptText;
            
        } catch (error) {
            console.log(`Could not load transcript for ${item.id}:`, error);
        }
    });
    
    await Promise.all(loadingPromises);
    console.log('Transcript text loaded into search store');
})();