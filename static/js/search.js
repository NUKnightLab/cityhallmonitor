var summaryTemplate = null;
var singleResultTemplate = null;
var multiResultTemplate = null;
var resultStatsTemplate = null;

$(function() {
    summaryTemplate = _.template($("#summary-template").html());
    singleResultTemplate = _.template($("#single-result-template").html());
    multiResultTemplate = _.template($("#multi-result-template").html());
    resultStatsTemplate = _.template($("#result-stats-sidebar").html());
    $('.example-search').click(function() {
        $('#search-input').val($(this).text());
        $('#search-submit').click();
        return false;
    });
    buildDateUI();
});

var addResult = function(obj) {
    var statusClass;
    switch (obj.docs[0].matter.status){
        case 'Adopted':
        case 'Approved':
        case 'Passed':
        case 'Recommended for Passage':
            statusClass = 'success';
            break;

        case 'Deferred and Published':
        case 'Direct Introduction':
        case 'In Committee':
        case 'Introduced':
        case 'Placed on File':
        case 'Recommended for Re-referral':
        case 'Re-referred':
            statusClass = 'warning';
            break;

        case 'Failed to Pass':
        case 'Recommended Do Not Pass':
        case 'Tabled':
        case 'Vetoed':
        case 'Void':
        case 'Withdrawn':
            statusClass = 'alert';
            break;
    }
    if(obj.docs.length > 1) {
        $(multiResultTemplate({docs: obj.docs, statusClass: statusClass})).appendTo('#search-results');
    } else {
        $(singleResultTemplate({doc: obj.docs[0], statusClass: statusClass})).appendTo('#search-results');
    }
};

var doSearch = function(searchUrl, subscribeUrl) {
    showLoadingState();

    var query = $('#search-input').val();
    var dateRangeType = $('#date-range-type').val();
    var ignoreRoutine = $('#ignore-routine').is(':checked');

    var queryQualifier = '';

    switch (dateRangeType) {
        case 'past-year':
            queryQualifier = ' in the past year';
            break;

        case 'past-month':
            queryQualifier = ' in the last 30 days';
            break;

        case 'any':
            break;
    }

    console.log('EXECUTING QUERY:: ' + query);

    $.ajax({
        url: searchUrl,
        data: {
            query: query,
            date_range: dateRangeType,
            ignore_routine: ignoreRoutine
        }
    })
    .success(function(data) {
        console.log(data);

        var groups = {};
        var dates = [];
        var dt = null;

        var totalDocuments = 0;
        var statTypes = {
            'Statuses': 'status',
            'Matter Types': 'type'
        };
        var statsData = {};

        $.each(data.documents, function(i, doc) {
            dt = doc.sort_date;

            if(dates.indexOf(dt) < 0) {
                dates.push(dt);
                groups[dt] = {};
            }
            if(doc.matter.id in groups[dt]) {
                groups[dt][doc.matter.id]['docs'].push(doc);
            } else {
                groups[dt][doc.matter.id] = {
                    'docs': [doc]
                };
            }

            $.each(statTypes, function(key, matter_field) {
                if (!(key in statsData)){
                    statsData[key] = {};
                }
                if(doc.matter[matter_field] in statsData[key]) {
                    statsData[key][doc.matter[matter_field]] += 1;
                } else {
                    statsData[key][doc.matter[matter_field]] = 1;
                }
            });
        });

        $('#results-summary').html($(summaryTemplate({
            total: data.documents.length,
            query: query,
            qualifier: queryQualifier
        })));

        $('#search-subscribe-form').submit(function(event) {
            handle_subscribe(event, subscribeUrl);
            return false;
        });

        if(data.documents.length > 0) {
            dates.sort(function(a,b) { return (b < a) ? -1 : 1 });
            for (i=0; i<dates.length; i++) {
                var dateGroups = groups[dates[i]];
                $.each(dateGroups, function(j, g) {
                    addResult(g);
                });
            }
        }
        $("#search-results").foundation('reveal', 'reflow');
        $('body,html').animate({scrollTop: $('#page-topper').outerHeight() + $('nav').outerHeight()}, 350);

        if (statsData) {
            $('#results-stats').html(resultStatsTemplate({statsData: statsData}));
        }
    })
    .error(function(xhr, status, errMsg) {
        alert(errMsg);
    })
    .complete(function(xhr, status) {
        hideLoadingState();
        $('#email-trigger').on('click', function(){
          $('#sub-box').slideToggle();
        });
    });

}; // doSearch
