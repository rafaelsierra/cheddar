(function(window, document, $, urls){

    /**
     * Moves to the next or first post, or highlights the next button
     */
    function move_cursor_to_next(){
        // Checks if there is a post active
        var article = $("article.active");
        var next;
        if(article.length > 0){
            next = article.next('article');
            if(next.length==0){
                $("article.active").removeClass("active");
                $(document).scrollTop($("a.next").offset().top)
                $("a.next").addClass("glow").focus();
            }else{
                next.click();
                $("a.next").removeClass("glow");
            }
        }else{
            if($("a.next.glow").length > 0){
                $("a.next.glow").click();
            }else{
                $("#postlist article").first().click();
            }
        }
    }
    
    function move_cursor_to_previous(){
        // TODO: Previous button
        var article = $("article.active");
        var prev;
        if(article.length == 0){
            if($("a.next.glow").length > 0){
                prev = $("#postlist article").last();
            }else{
                return;
            }
        }else{
            prev = article.prev('article');
        }
        prev.addClass("active");
        prev.click();
        $("a.next").removeClass("glow");
    }

    /**
     * Mark the post as read and highlight it
     */
    function read_post(){
        $this = $(this);
        $("article.active").removeClass('active');
        $this.addClass('active');
        
        $(document).scrollTop($this.offset().top-10);
        
        return;
        $("#postlist .active").removeClass("active");
        article.addClass("active");
        var post_content = article.find('.post-content');
        var site = $("#site-"+article.data('site_id'));
        var counter = site.find('.unread-counter');

        if(!article.hasClass('post-read')){
            counter.text(counter.text()-1);
            $.cheddar('markAsRead', article.data("post_id"));
        }
        
        window.location.hash = 'post-'+article.data('post_id');
        window.scrollBy(0, -55);
        
        var unread_posts = $("#postlist article:not(.post-read)");
        if(unread_posts.length == 0){
            post_list_state.since = $("#postlist article:last-child").data("created_at");
            $.cheddar('loadPosts');
        }
    }

    $(document).ready(function() {
        $("article.post").click(read_post);
        $(document).bind('keypress', 'j', move_cursor_to_next);
        $(document).bind('keypress', 'k', move_cursor_to_previous);
    }); 
    
    
})(window, document, jQuery, urls);

