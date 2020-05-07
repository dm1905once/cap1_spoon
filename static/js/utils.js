// recipeSummary = $('.recipe-summary').text()
// $('.recipe-summary').html(recipeSummary)


$('.recipe-summary').each(function() {
    recipe = $(this).text()
    $(this).html(recipe)
})