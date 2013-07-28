(function(window, document, $, urls){
	
	var console = 'console' in window?window.console:{'log':function(m){}}
	
    function save_new_folder(select){
        var li = $(select).parent().parent();
        var data = {'usersite_id': li.data('usersite_id'), 'folder_id': select.value}
        li.removeClass("pulse");
        $(".loading").show();
        $.post(urls.change_folder, data, function(response){
            if(response.success){
                $(".loading").hide();
                li.addClass("pulse");
            }
        }, 'json')
    }
    
    $(document).ready(function(){
        $("select").on({
            'change': function(){
                save_new_folder(this);
            }
        })
        
        $("#add-folder").on('submit', function(){
            $(".loading").show();
            var form = $(this);
            $.post(this.action, $(this).serialize(), function(response){
                if(response.success){
                    form.parent().addClass("pulse");
                    window.location.reload();
                }
            }, 'json');
            return false;
        })
        
        
        $(".unsubscribe-form").submit(function(){
        	// TODO: Use modal
        	
        	var li = this.parentElement;
        	var site_title = $(li).find(".site-title").text()
        	if(!confirm(gettext("Unsubscribe from "+site_title+"?"))){
        		return false;
        	}
        	
        	$.post(this.action, $(this).serialize(), function(response){
        		if(response.success){
        			alert(gettext("Unsubscribed from "+site_title))
        			$(li).slideUp(function(){
        				$(li).remove();
        			})
        		}else{
        			alert(gettext('Failed trying to unsubscribe.\nCheck console for details.'))
        			console.log(response)
        		}
        	}, 'json')
        	return false;
        })
    })
})(window, document, jQuery, urls);