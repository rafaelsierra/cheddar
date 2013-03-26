/*
 * This script, yet seems like a jQuery plugin, is pretty much linked with
 * every HTML tag in the site, I just did for the sake of organization 
 */
(function($) {
    var urls = {
        'STATIC_URL': '{{STATIC_URL|escapejs}}',
        'MEDIA_URL': '{{MEDIA_URL|escapejs}}',
        'mysites': "{% url 'feeds:my-sites' %}"
    };
    
    var methods = {
        init: function(options){
            // Nothing to do here!
        },
        
        loadSites: function(){
            $.ajax({
                url: urls.mysites,
                dataType: 'html',
                success: function(response){
                    // Clear the current list of sites
                    $("#feed-list li.nav-header").siblings().remove();
                    // Loads the new one
                    $("#feed-list").append(response);
                }
            })
        }
    };

    $.cheddar = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if ( typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.cheddar');
        }
    };

})(jQuery); 