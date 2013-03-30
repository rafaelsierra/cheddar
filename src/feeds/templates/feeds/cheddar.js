/*
 * This script, yet seems like a jQuery plugin, is pretty much linked with
 * every HTML tag in the site, I just did for the sake of organization 
 */
(function($) {

    var urls = {
        'STATIC_URL': '{{STATIC_URL|escapejs}}',
        'MEDIA_URL': '{{MEDIA_URL|escapejs}}',
        'mysites': "{% url 'feeds:my-sites' %}",
        'post_list_read': "{% url 'feeds:post-list-read' %}",
        'post_list_unread': "{% url 'feeds:post-list-unread' %}",
        'mark_post_as_read': "{% url 'feeds:post-mark-as-read' %}"
    };
    
    var post_list_state = {
        is_read: false,
        page: 1,
        site: null,
    };
    
    var navigation_state = {current_post:null};

    function read_post(article){
        // Open and mark post as read
        var post_content = article.find('.post-content');
        var site = $("#site-"+article.data('site_id'));
        var counter = site.find('.unread-counter');

        if(!article.hasClass('post-read')){
            counter.text(counter.text()-1);
            $.cheddar('markAsRead', article.data("post_id"));
        }
        
        window.location.hash = article.attr('id');
    }
    
    
    function move_cursor_to(next_or_previous){
            var current_post;  
            if(!navigation_state.current_post){
                navigation_state.current_post = $("#postlist article.post").first();
            }else{
                if(next_or_previous == 'next'){
                    var next =  navigation_state.current_post.next();
                    if(next){
                        navigation_state.current_post = next;
                    }
                }else{
                    var previous;
                    if(previous){
                        navigation_state.current_post = previous;
                    }
                    
                }
            }
            navigation_state.current_post.find('header').click();            
    }
    
    function move_cursor_to_next(){
        move_cursor_to('next');
    }
    function move_cursor_to_previous(){
        move_cursor_to('previous');
    }
        
    var methods = {
        init: function(options){
            $("#postlist").on('click', 'article.post header', function(){
                read_post($(this).parent());
            });
            
            $(document).bind('keypress', 'j', move_cursor_to_next);
            $(document).bind('keypress', 'k', move_cursor_to_previous);
            $(document).bind('keypress', 'r', function(){
                $.cheddar('refresh');
            });
            
            return this;
        },
        
        loadSites: function(){
            $.ajax({
                url: urls.mysites,
                dataType: 'html',
                success: function(response){
                    // Clear the current list of sites
                    $("#feed-list").siblings().remove();
                    // Loads the new one
                    $("#feed-list").parent().append(response);
                }
            });
            return this;
        },
        
        loadPosts: function(){
            var data = {};
            data['page'] = post_list_state.page;
            if(post_list_state.site){
                site['site'] = post_list_state.site;
            }
            
            $.ajax({
                url: post_list_state.is_read?urls.post_list_read:urls.post_list_unread,
                'data': data, // That's why I hate this with javascript
                success: function(response){
                    $("#postlist").append(response);
                    // Change all <a> to target=_blank
                    $("#postlist .post-content a").attr('target', '_blank');
                },
                dataType: 'html'
                
            });
            return this;
        },
        
        markAsRead: function(post_id){
            // Mark this post as read
            $.post(urls.mark_post_as_read, {id:post_id} ,function(response){
                $("#post-"+post_id).addClass('post-read');
            }, 'json');
        },
        
        refresh: function(){
            $("#feed-list").siblings().remove();
            $("#postlist").html('');
            $.cheddar('loadSites').cheddar('loadPosts');
            navigation_state.current_post = null;
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