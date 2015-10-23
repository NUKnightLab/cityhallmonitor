var summaryTemplate = null;
var singleResultTemplate = null;
var multiResultTemplate = null;

$(function() {
    summaryTemplate = _.template($("#summary-template").html());
    singleResultTemplate = _.template($("#single-result-template").html());
    multiResultTemplate = _.template($("#multi-result-template").html());
    $('.example-search').click(function() {
        $('#search-input').val($(this).text());
        $('#search-submit').click();
        return false;
    });
    buildDateUI();
});

var addResult = function(obj) {
    if (obj.docs.length > 1) {
      $(multiResultTemplate({ docs: obj.docs })).appendTo('#search-results');
    } else {
      $(singleResultTemplate({ doc: obj.docs[0] })).appendTo('#search-results');
    }
};

var doSearch = function(subscribeUrl) {
    showLoadingState();
    var DATE_FORMAT = 'YYYY-MM-DD 00:00:00+00:00';
    var MONTH_FORMAT = 'YYYY-MM';
    var dateRangeType = $('#date-range-type').val();
    var query = $('#search-input').val();
    var startDate = moment();
    var endDate = moment();
    var queryExtra = '';
    var queryQualifier = '';
    var ignoreRoutine = $('#ignore-routine').is(':checked');
    var routineFilter = '';
    if ($('#ignore-routine').is(':checked')) {
        routineFilter
        += ' !"Congratulations extended"'
        + ' !"Gratitude extended"'
        + ' !"Recognition extended"'
        + ' !"Issuance of permits for sign(s)"'
        + ' !"Sidewalk cafe(s) for"'
        + ' !"Canopy(s) for"'
        + ' !"Awning(s) for"'
        + ' !"Residential permit parking"'
        + ' !"Handicapped Parking Permit"'
        + ' !"Handicapped permit"'
        + ' !"Grant(s) of privilege in public way"'
        + ' !"Loading/Standing/Tow Zone(s)"'
        + ' !"Senior citizens sewer refund(s)"'
        + ' !"Oath of office"';
    }
    switch (dateRangeType) {
        case 'past-year':
            startDate.subtract(1, 'years');
            var iterDate = moment();
            while (iterDate.format(MONTH_FORMAT) >= startDate.format(MONTH_FORMAT)) {
                queryExtra += ' MatterSortMonth: ' + iterDate.format(MONTH_FORMAT);
                iterDate.subtract(1, 'months');
            }
            queryQualifier = ' in the past year';
            break;
        case 'past-month':
            startDate.subtract(30, 'days');
            queryExtra += 'MatterSortMonth: ' + startDate.format(MONTH_FORMAT);
            if (endDate.format(MONTH_FORMAT) !== startDate.format(MONTH_FORMAT)) {
                queryExtra += ' MatterSortMonth: ' + endDate.format(MONTH_FORMAT);
            }
            queryQualifier = ' in the last 30 days';
            break;
        case 'any':
            // no queryExtra for all dates
            break;
    }
    query += ' account:12872-knight-lab project:"Chicago City Hall Monitor"';
    query += ' ' + queryExtra + routineFilter;
    console.log('EXECUTING DOCUMENTCLOUD QUERY:: ' + query);
    $.ajax({
        url: 'https://www.documentcloud.org/api/search.json?q='
        + query + '&per_page=1000&data=true'
    })
    .success(function(data) {
        var groups = {};
        var dates = [];
        var startDateStr = startDate.format(DATE_FORMAT);
        var dt = null;
        $.each(data.documents, function(i, doc) {
            dt = doc.data.MatterSortDate;
            if (dateRangeType !== 'any' && dt < startDateStr) {
                return true;
            }

            if(dates.indexOf(dt) < 0) {
                dates.push(dt);
                groups[dt] = {};
            }

            if(doc.data.MatterId in groups[dt]) {
                groups[dt][doc.data.MatterId]['docs'].push(doc);
            } else {
                groups[dt][doc.data.MatterId] = {
                    'data': doc.data,
                    'docs': [doc]
                };
            }
        });

        $('#results-summary').html($(summaryTemplate({
            total:data.total,
            query: $('#search-input').val(),
            qualifier: queryQualifier
        })));

        $('#search-subscribe-form').submit(function(event) {
            handle_subscribe(event, subscribeUrl);
            return false;
        });

        if(data.documents.length) {
            dates.sort(function(a,b) { return (b < a) ? -1 : 1 });
            for (i=0; i<dates.length; i++) {
                var dateGroups = groups[dates[i]];
                $.each(dateGroups, function(j, g) {
                    addResult(g);
                });
            }
        }
        $("#search-results").foundation('reveal', 'reflow');
        hideLoadingState();
    });
}; // doSearch
