
function sortTable(sortKey, sortOrder) {
    let url = new URL(window.location.href);
    
    url.searchParams.delete('clear');
    url.searchParams.set('sort_key', sortKey);
    url.searchParams.set('sort_order', sortOrder);
    
    window.location.href = url.href;
}