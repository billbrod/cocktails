document$.subscribe(function() {
    function capitalize(string) {
        return string.split(' ').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' ')
    }
    // get the original serves value
    const parse_serves = RegExp('Drinks: +([0-9]+)(.*)')
    orig = parse_serves.exec($('#serves').text())
    // only do this if we can find the serves section, otherwise the exception
    // blocks loading of all other javascript
    if (orig !== null) {
        $.getJSON('./../prices.json', function(prices) {
            $.getJSON('./../ingredients.json', function(ingredients) {
                $('.ingredient').each(function(idx, elem) {
                    if ($(elem).text().indexOf('[') > -1) {
                        // then extract the values within the brackets
                        ingr =  $(elem).text()
                        ingr = ingr.substring(ingr.indexOf('[')+1, ingr.indexOf(']')).split(',')
                        ingr = ingr.map(d => d.trim().toLowerCase())
                        $(elem).text($(elem).text().split('[')[0])
                    } else {
                        ingr = $(elem).html().split('(')[0].split('<a>')[0].trim().toLowerCase()
                        $(elem).attr('ingredient-name', ingr)
                        ingr = ingredients[ingr]
                    }
                    if (ingr !== undefined) {
                        price = ingr.map(d => convert_prices(prices[d]))
                        dropdown = ingr.map((d, i) => `<option ingredient-price=${price[i]}>${capitalize(d)}</option>`).join('')
                        const slct = `<select class="form-select ingredient-select">${dropdown}</select>`
                        $(elem).append(slct)
                    } else {
                        ingr = $(elem).attr('ingredient-name')
                        $(elem).attr('ingredient-price', convert_prices(prices[ingr]))
                    }
                })
                price_out()
                $('.ingredient-select').on('change', price_out)
            })
        })
        function convert_prices(price) {
            if (price !== undefined) {
                vol_oz = convert_volumes(price[1], price[2])
                price_oz = parseFloat(price[0]) / vol_oz
                return price_oz.toFixed(2)
            } else {
                return 0
            }
        }
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
                                  'ml': .035, 'mL': .035, 'oz': 1})
            return parseFloat(val) * conversions[unit]
        }
        const sum_others = function(){
            return $.map($('.ingredient-num').not('.ingredient-oz'), function(ingr) {
                return convert_volumes(parseFloat($(ingr).text()), $(ingr).next().text())
            }).reduce((sum, next) => sum+next, 0)
        }
        const price_out = function() {
            $('.ingredient-price').each(function(idx, elem) {
                // this is the ingredient column in the same row. it might have
                // a select element, in which case, we grab the price from the
                // selected one. else, grab price from the whole row.
                ingr = $(elem).prev()
                if (ingr.find('select').length > 0) {
                    oz_price = ingr.find('select option:selected').attr('ingredient-price')
                } else {
                    oz_price = ingr.attr('ingredient-price')
                }
                ingr_num = parseFloat($($(elem).siblings()[0]).text())
                ingr_measure = $($(elem).siblings()[1]).text()
                ingr_oz = convert_volumes(ingr_num, ingr_measure)
                price = (parseFloat(oz_price) * ingr_oz).toFixed(2)
                // if price is NaN, just use the empty string
                price = isNaN(price) ?  "" : "$" + price
                $(elem).text(price)
            })
            const price_sum = $.map($('.ingredient-price'), function(val) {
                // if there are any NaNs (or anything else we can't cast to
                // float), use 0 instead, ignoring the first character, since
                // that's a dollar sign
                return parseFloat($(val).text().slice(1)) || 0
            }).reduce((sum, next) => sum+next, 0)
            $('#total-price').text("$" + price_sum.toFixed(2))
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
            price_out()
        })
    }
})
