// Substitute html fiels to actually display their html tags

$('.recipe-summary').each(function() {
    recipe = $(this).text()
    $(this).html(recipe)
})


// Home page: filter the Search By Ingredients select by typing into a textbox
jQuery.fn.filterByText = function(textbox, selectSingleMatch) {
    return this.each(function() {
        var select = this;
        var options = [];
        $(select).find('option').each(function() {
            options.push({value: $(this).val(), text: $(this).text()});
        });
        $(select).data('options', options);
        $(textbox).bind('change keyup', function() {
            var options = $(select).empty().data('options');
            var search = $.trim($(this).val());
            var regex = new RegExp(search,"gi");
          
            $.each(options, function(i) {
                var option = options[i];
                if(option.text.match(regex) !== null) {
                    $(select).append(
                       $('<option>').text(option.text).val(option.value)
                    );
                }
            });
            if (selectSingleMatch === true && $(select).children().length === 1) {
                $(select).children().get(0).selected = true;
            }
        });            
    });
};

$(function() {
    $('#ingredients').filterByText($('#textbox'), true);
});  