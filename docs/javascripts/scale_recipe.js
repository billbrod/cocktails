document$.subscribe(function() {
    // get the original serves value
    const parse_serves = RegExp('Drinks: +([0-9]+)(.*)')
    orig = parse_serves.exec($('#serves').text())
    // only do this if we can find the serves section, otherwise the exception
    // blocks loading of all other javascript
    if (orig !== null) {
        $('#serves').attr('data-original', orig[1])
        $('#serves').text(orig[0].replace(orig[1], '  ').replace(orig[2], ''))
        // create the +/- buttons
        // these two svgs are based on the material-plus and material-minus icons
        const plus = '<span class="twemoji"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2Z"></path></svg></span>'
        const minus = '<span class="twemoji"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 13H5v-2h14v2Z"></path></svg></span>'
        const increment = function(){
            $('#serves-input').val(parseInt($('#serves-input').val())+1)
            $('#serves-input').trigger("change")
        }
        const decrement = function(){
            $('#serves-input').val(parseInt($('#serves-input').val())-1)
            $('#serves-input').trigger("change")
        }
        const plus_button = '<a id="plus-button" class="md-button md-button--primary" style="padding: .5em .7em;">' + plus + '</a>'
        const minus_button = '<a id="minus-button" class="md-button md-button--primary" style="padding: .5em .7em;">' + minus + '</a>'
        const input = '<input class="md-typeset form-control" type="text" min="0" id="serves-input">'
        $('#serves').append(minus_button)
        $('#minus-button').click(decrement)
        $('#serves').append(input)
        $('#serves-input').val(parseInt(orig[1]))
        $('#serves').append(plus_button)
        $('#serves').append(orig[2])
        $('#plus-button').click(increment)
        const scale_input = '<input class="md-typeset form-control scale-input" type="text" min="0" id="scale-input">'
        const ml_button = '<input id="ml_button" class="md-typeset btn-check" type="radio" name="scale_button" value="mL">'
        const ml_label = '<label for="ml_button" class="md-typeset btn btn-outline-primary">mL</label>'
        const oz_button = '<input id="oz_button" class="md-typeset btn-check" type="radio" name="scale_button" value="oz" checked="">'
        const oz_label = '<label for="oz_button" class="md-typeset btn btn-outline-primary">oz</label>'
        $('#scale').append(scale_input)
        $('#scale').append(oz_button)
        $('#scale').append(oz_label)
        $('#scale').append(ml_button)
        $('#scale').append(ml_label)
        // to get current checked:
        // encode original ingredient values
        $('.ingredient-num').each(function(idx, elem){
            orig = $(elem).attr("data-original", $(elem).text())
        })
        const scale_up = function(){
            tgt_oz = convert_volumes($('#scale-input').val(),
                                     $('input[name=scale_button]:checked').attr('value'))
            single_serv = $('#total_vol_oz').attr('data-original')
            n_drinks = parseInt(tgt_oz / single_serv)
            $('#serves-input').val(n_drinks).change()
        }
        $('#scale-input').on('change', scale_up)
        $('input[name=scale_button]').on('change', scale_up)
        $('input[name=scale_button]').on('change', function() {
            if ($('input[name=scale_button]:checked').attr('value') === "mL") {
                convert = 1/.035
            } else {
                convert = .035
            }
            $('#scale-input').val($('#scale-input').val() * convert).change()
        })
        const sum_oz = function(){
            return $.map($('.ingredient-oz'), function(ingr) {
                return parseFloat($(ingr).text())
            }).reduce((sum, next) => sum+next, 0)
        }
        const convert_volumes = function(val, unit) {
            conversions = Object({'dash': .021, 'tsp': 1/6, 'Tbsp': .5, 'Garnish': 0,
                                  'mL': .035, 'oz': 1})
            return parseFloat(val) * conversions[unit]
        }
        const sum_others = function(){
            return $.map($('.ingredient-num').not('.ingredient-oz'), function(ingr) {
                return convert_volumes(parseFloat($(ingr).text()), $(ingr).next().text())
            }).reduce((sum, next) => sum+next, 0)
        }
        $('#total_vol_oz').text(`${sum_oz().toFixed(3)}`)
        $('#total_vol_oz').attr('data-original', `${sum_oz().toFixed(3)}`)
        $('#total_vol_all').text(`${(sum_others() + sum_oz()).toFixed(3)}`)
        $('#total_vol_all').attr('data-original', `${(sum_others() + sum_oz()).toFixed(3)}`)
        // when the serves number changes, update the individuals and the total
        $('#serves-input').on("change", function(){
            orig = $('#serves').attr('data-original')
            new_val = $('#serves-input').val()
            ratio = parseFloat(new_val) / parseFloat(orig);
            $(".ingredient-num").each(function(idx, elem){
                orig = $(elem).attr('data-original').split('-')
                new_val = $(elem).text().split('-').map((x, i) => (parseFloat(orig[i])*ratio).toFixed(2)).join('-')
                $(elem).text(new_val)
            })
            $('#total_vol_oz').text(`${sum_oz().toFixed(3)}`)
            $('#total_vol_all').text(`${(sum_others() + sum_oz()).toFixed(3)}`)
        })
    }
})
