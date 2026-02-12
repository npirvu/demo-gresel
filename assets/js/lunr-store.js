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
{%- if item.object_location -%}"object_location": {{ item.object_location | jsonify }},{%- endif -%}
"ocr_text": "",
"id": {% if item.parentid %}{{ item.parentid | append: '.html#' | append: item.objectid | jsonify }}{% else %}{{item.objectid | append: '.html' | jsonify }}{% endif %}

}{%- unless forloop.last -%},{%- endunless -%}
{%- endfor -%}
];

// Load OCR text from JSON files
(async function loadOCRText() {
    const loadingPromises = store.map(async (item) => {
        try {
            if (!item.object_location) {
                return;
            }
            
            const response = await fetch(`{{ '/' | relative_url }}${item.object_location}`);
            
            if (!response.ok) {
                return;
            }
            
            const jsonData = await response.json();
            
            if (jsonData.pages && Array.isArray(jsonData.pages)) {
                const allText = [];
                
                jsonData.pages.forEach(page => {
                    if (page.textRegions && Array.isArray(page.textRegions)) {
                        page.textRegions.forEach(region => {
                            if (region.text && region.text.trim().length > 0) {
                                allText.push(region.text);
                            }
                            if (region.textLines && Array.isArray(region.textLines)) {
                                region.textLines.forEach(line => {
                                    if (line.text && line.text.trim().length > 0) {
                                        allText.push(line.text);
                                    }
                                });
                            }
                        });
                    }
                });
                
                item.ocr_text = allText.join(' ');
            }
            
        } catch (error) {
            console.log(`Could not load OCR for ${item.id}:`, error);
        }
    });
    
    await Promise.all(loadingPromises);
    console.log('OCR text loaded into search store');
})();