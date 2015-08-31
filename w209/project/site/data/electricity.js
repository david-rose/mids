

function loaddata()
{
    var req = new XMLHttpRequest();
    // make an asynchronous call to retrieve the electricity data
    req.open("GET", "./data/electricity_data.json", false);
    req.send(null);
    return JSON.parse(req.responseText);
}

function getdescription(name)
{
    return ((descriptions[name] == null) ? capitalize(name) : descriptions[name]);
}
function capitalize(s)
{
    return s.charAt(0).toUpperCase() + s.slice(1);
}

function isnumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function getregion(name)
{
    var d = data[name];
    var r = name;
    if (d.iscountry == 'Y')
    {
        r = d.subregion;
    }
    return r;
}

function getunits(valuetype, population)
{
    // determine the multiplier to use for per capita units
    var mult = 1;
    var units = "MkWh";
    if (valuetype == 'percap') {
        if (population > 0)
        {
            //mult = 1000000 / Number(population);
            mult = 1000 / Number(population);
            units = "kWh per capita"
        }
        else // no population data available
        {
            mult = 0;
            units = "kWh per capita"
        }
    }
    return {'units': units, 'mult': mult};
}

function getflowtypes(flow)
{
    var flowlist = [];
    if (flow == "consumption")
    {
        flowlist = ['Total Consumption', 'Exports', 'Lost or Stored', 'Consumption Imbalance'];
    }
    else if (flow == 'Total Consumption')
    {
        flowlist = ['Households', 'Services', 'Energy Industry', 'Non-Energy Industries',
                    'Transportation', 'Agriculture', 'Other Consumption'];
    }
    else if (flow == "production")
    {
        flowlist = ['Total Production', 'Imports', 'Production Imbalance'];
    }
    else if (flow == "Total Production")
    {
        flowlist = ['Renewable', 'Non-Renewable'];
    }
    else if (flow == "Renewable")
    {
        flowlist = renewables; // defined in electricity_codes.js
    }
    else if (flow == "Non-Renewable")
    {
        flowlist = nonrenewables; // defined in electricity_codes.js
    }
    else
    {
        flowlist = [];
    }
    return flowlist;
}

function getwheeldata(name, selectedyear, valuetype, adjoining)
{
    var wheeldata = [];
    var yearlist = getyearlist(selectedyear, adjoining)
    for (var i = 0; i < yearlist.length; i++)
    {
        var year = yearlist[i];
        var r = new Object();
        r['name'] = name;
        r['year'] = year;
        r['selected'] = (year == selectedyear) ? 'Y' : 'N';
        if (year >= minyear && year <= maxyear)
        {
            var facts = data[name][year];
            r['population'] = facts.population;
            var units = getunits(valuetype, r.population);
            r['electricity'] = (units.mult * facts.electricity).toFixed(0);
            r['units'] = units.units;
        }
        else
        {
            r['year'] = "";
            r['population'] = "";
            r['electricity'] = "0";
            r['units'] = "";
        }
        wheeldata.push(r);
    }
    return wheeldata;
}

var minyear = 1990;
var maxyear = 2012;
function getyearlist(selectedyear, adjoining)
{
    // generate list of years
    // if adjoining < 0, return all years
    var selectedyear = parseInt(selectedyear);
    var yearlist = [];
    //var padding = 3 // number of extra years to facilitate wheel widget
    //var start = minyear - padding;
    //var end = maxyear + padding;
    //var start = minyear;
    //var end = maxyear;
    if (adjoining >= 0)
    {
        // start = Math.max(selectedyear - adjoining, minyear);
        // end =   Math.min(selectedyear + adjoining, maxyear);
        start = selectedyear - adjoining;
        end =   selectedyear + adjoining;
    }
    //for (var i = maxyear; i >= minyear; i--)
	for (var i = minyear; i <= maxyear; i++)
    {
        yearlist.push(String(i));
    }
    return yearlist;
}

var SankeyNode = function(node, name)
{
    this.node = node;
    this.name = name;
}
var SankeyLink = function(source, target, region, flow)
{
    this.source = source;
    this.target = target;
    this.value = 0;
    this.percentage = 0;
    this.region = region;
    this.flow = flow;
    this.units = '';
}

function getsankeydata(name, selectedyear, valuetype, flow, hierarchy, direction)
// Call: getsankeydata(region, year, valuetype, 'production'/'consumption', hierarchy, 'left'/'right');
{
    var sankeydata = [];
    var flowtypes = getflowtypes(flow);
    var nodes = [];
    var links = [];
    var subregions = getsubregions(name);
    for (var i = 0; i < flowtypes.length; i++)
    {
        nodes.push(new SankeyNode(nodes.length, 'PushOut' + (nodes.length + 1).toString()));
    }
    for (var i = 0; i < flowtypes.length; i++)
    {
        var flow = flowtypes[i];
        nodes.push(new SankeyNode(nodes.length, flow));
        links.push(new SankeyLink(flow, 'PushOut' + (i + 1).toString(), name, flow));
    }
    if (hierarchy == 'energy' || subregions.length == 0)
    {
        for (var i = 0; i < flowtypes.length; i++)
        {
            var flow = flowtypes[i];
            var subtypes = getflowtypes(flow);
            for (var j = 0; j < subtypes.length; j++)
            {
                var subflow = subtypes[j];
                nodes.push(new SankeyNode(nodes.length, subflow));
                links.push(new SankeyLink(subflow, flow, name, subflow));
                if (subregions.length > 0)
                {
                    for (var k = 0; k < subregions.length; k++)
                    {
                        links.push(new SankeyLink(subregions[k], subflow, subregions[k], subflow));
                    }
                }
                else // this is a country, not a region
                {
                    // add further details
                    var subsubflows = getflowtypes(subflow);
                    for (var k = 0; k < subsubflows.length; k++)
                    {
                        subsubflow = subsubflows[k];
                        nodes.push(new SankeyNode(nodes.length, subsubflow));
                        links.push(new SankeyLink(subsubflow, subflow, name, subsubflow));
                    }
                }
            }
        }
        // add regions/countries to node list last
        for (var i = 0; i < subregions.length; i++)
        {
            nodes.push(new SankeyNode(nodes.length, subregions[i]));
        }
    }
    else // hierarchy equals 'region'
    {
        for (var i = 0; i < flowtypes.length; i++)
        {
            var flow = flowtypes[i];
            for (var k = 0; k < subregions.length; k++)
            {
                var subregion = subregions[k];
                links.push(new SankeyLink(subregion, flow, subregion, flow));
                var subtypes = getflowtypes(flow);
                for (var j = 0; j < subtypes.length; j++)
                {
                    var subflow = subtypes[j];
                    links.push(new SankeyLink(subflow, subregion, subregion, subflow));
                }
            }
        }
        // add regions/countries to node list
        for (var i = 0; i < subregions.length; i++)
        {
            nodes.push(new SankeyNode(nodes.length, subregions[i]));
        }
        // add flowtypes to node list last
        for (var i = 0; i < flowtypes.length; i++)
        {
            var subtypes = getflowtypes(flowtypes[i]);
                for (var j = 0; j < subtypes.length; j++)
                {
                    var subflow = subtypes[j];
                    nodes.push(new SankeyNode(nodes.length, subflow));
                }
        }
    }
    // set the electricity values and set the percentages
    setsankeyvalues(links, selectedyear, valuetype);
    // for 'right' side sankey need to reverse the source and target values
    if (direction == 'right')
    {
        reversesourceandtarget(links);
    }
    return {'nodes':nodes, 'links':links};

}
function reversesourceandtarget(links)
{
    for (var i in links)
    {
        var link = links[i];
        var tmp = link.target;
        link.target = link.source;
        link.source = tmp;
    }
}
function setsankeyvalues(links, selectedyear, valuetype)
{
    flowtotals = {}; // maintain totals for each flow type
    for (var i in links)
    {
        var link = links[i];
        var rdata = data[link.region][selectedyear];
        var units = getunits(valuetype, rdata.population);
        var target = link.target;
        // combine all PushOutX values as one
        if (target.substring(0,7).toLowerCase() == 'pushout')
        {
            target = 'pushout';
        }
        link.value = rdata[link.flow] * units.mult;
        link.units = units.units;
        if (typeof flowtotals[target] == 'undefined')
        {
            flowtotals[target] = link.value;
        }
        else
        {
            flowtotals[target] += link.value;
        }
    }
    // now set percents
    for (i in links)
    {
        var link = links[i];
        var target = link.target;
        if (target.substring(0,7).toLowerCase() == 'pushout')
        {
            target = 'pushout';
        }
        var total = flowtotals[target];
        if (total > 0)
        {
            link.percentage = (100 * (link.value / total)).toFixed(2);
        }
    }
}
                        
        
function getsubregions(name)
{
    var children = [];
    if (name == 'World')
    {
        children = Object.keys(regions).sort();
    }
    else
    {
        var parent = data[name];
        if (parent.isregion == 'Y')
        {
            children = Object.keys(regions[name]).sort();
        }
        else if (parent.issubregion == 'Y')
        {
            children = regions[parent.region][name];

        }
        else if (parent.iscountry == 'Y')
        {
            children = [];
        }
    }
    return children;
}

var lowthreshold = 2; // minimum percent value, anything less gets aggregated
var maxsankey = 5; // maximum number of individual records to display, aggregate the rest
function aggregate(o, proto)
{
    for (var i = 0; i < o.length; i++)
    {
        var v = o[i];
        if (typeof v.children == 'object' && v.children.length > 0)
        {
            v.children = aggregate(v.children, v);
        }
    }
    // sort in order of percent
    o.sort(sortbypercent);
    var newlist = [];
    var r = new SankeyObj(proto.otype);
    r.georegion = proto.georegion;
    r.flow = proto.flow;
    r.name = 'Other';
    r.year = proto.year;
    r.units = proto.units;
    for (var i = 0; i < o.length; i++)
    {
        var v = o[i];
        var p = v.percent;
        if (p < lowthreshold || i >= maxsankey)
        {
            r.value += v.value;
            r.description += (r.description == '') ? capitalize(v.name) : ', ' + capitalize(v.name);
            r.percent += v.percent;
        }
        else
        {
            newlist.push(v);
        }
    }
    if (r.value > 0)
    {
        newlist.push(r);
    }
    return newlist;
}

function sortbypercent(x, y)
{
    // sort by 'percent' field in decreasing order
    return (sortby(x, y, 'percent') * -1);
}

function sortby(x, y, field)
{
    var xp = x[field];
    var yp = y[field];
    r = 0; // default is equals
    if (xp < yp)
    {
        r = -1;
    }
    else if (xp > yp)
    {
        r = 1;
    }
    return r;
}


var TopFive = function(category, year, units)
{
    this.category = category;
    this.year = year;
    this.total = 0;
    this.units = units;
    this.countries = [];
    this.addcountry = function(country)
    {
        this.countries.push(country);
        if (this.units == null)
        {
            this.units = country.units;
        }
    };
    this.settopfive = function(direction)
    {
        if (direction == 'desc')
        {
            this.countries.sort(sortbyvaluedescending);
        }
        else
        {
            this.countries.sort(sortbyvalueascending);
        }
        for (var i = 0; i < 5 && i < this.countries.length; i++)
        {
            this.countries[i].rank = (i + 1);
            this.total += this.countries[i].value;
        }
        this.countries.splice(5, Number.MAX_VALUE);
    };
    this.maxvalue = function()
    {
        var maximum = 0;
        for (var i = 0; i < this.countries.length; i++)
        {
            if (this.countries[i].value > maximum)
            {
                maximum = this.countries[i].value;
            }
        }
        return maximum;
    }
};

var TopFiveCountry = function(name, rank, value, units)
{
    this.name = name;
    this.rank = rank;
    this.value = value;
    this.units = units;
}

function sortbyvaluedescending(x, y)
{
    // sort in descending order
    return (sortby(x, y, 'value') * -1);
}
function sortbyvalueascending(x, y)
{
    // sort in descending order
    return (sortby(x, y, 'value') * 1);
}

var topfivecategories = ['Total Production', 'Total Consumption', 'Renewable', 'Nuclear'];
function gettopfivedata(region, year, valuetype, flowlist, direction)
{
    var topfivedata = {};
    for (var i = 0; i < flowlist.length; i++)
    {
        category = flowlist[i];
        topfivedata[category] = new TopFive(category, year, null);
    }
    var yeardata = getcountryyeardata(region, year);
    for (var name in yeardata)
    {
        var yd = yeardata[name];
        var units = getunits(valuetype, yd.population);
        for (var i = 0; i < flowlist.length; i++)
        {
            var category = flowlist[i];
            var value = Math.round(units.mult * yd[category]);
            topfivedata[category].addcountry(new TopFiveCountry(name, 0, value, units.units));
        }
    }
    var tmp = [];
    for (var i = 0; i < flowlist.length; i++)
    {
        var category = flowlist[i];
        topfivedata[category].settopfive(direction);
        tmp.push(topfivedata[category]);
    }
    return tmp;
}
function gettopfivecountrieslist(year, valuetype, flow)
{
    var t5 = gettopfivecountries(year, valuetype, flow);
    countries = [];
    for (var i = 0; i < t5.countries.length; i++)
    {
        countries.push(t5.countries[i].name);
    }
    return countries;
}

function gettopfivecountries(year, valuetype, flow)
{
    var t5 = new TopFive(flow, year, null);
    var yeardata = getcountryyeardata(year);
    for (var name in yeardata)
    {
        var yd = yeardata[name];
        var units = getunits(valuetype, yd.population);
        var value = Math.round(units.mult * yd[flow]);
        t5.addcountry(new TopFiveCountry(name, 0, value, units.units));
    }
    t5.settopfive();
    return t5;
}

function getcountryyeardata(region, year)
{
    var countrylist = getcountriesinregion(region);
    // gather all yeardata objects
    var yeardata = {};
    for (var i = 0; i < countrylist.length; i++)
    {
        var region = data[countrylist[i]];
        // include only those for countries, not regions or aggregates
        if (region.iscountry == 'Y' && countrylist[i] != 'Micronesia') // hack for Micronesia
        {
            yeardata[countrylist[i]] = region[year];
        }
    }
    return yeardata;
}
function getcountryyeardata_old(region, year)
{
    // gather all yeardata objects
    var yeardata = {};
    var regionlist = Object.keys(data);
    for (var i = 0; i < regionlist.length; i++)
    {
        var region = data[regionlist[i]];
        // include only those for countries, not regions or aggregates
        if (region.iscountry == 'Y' && regionlist[i] != 'Micronesia') // hack for Micronesia
        {
            yeardata[regionlist[i]] = region[year];
        }
    }
    return yeardata;
}

function getcountriesinregion(name)
{
    var countrylist = [];
    var regionlist = [];
    var region = data[name];
    if (name == 'World')
    {
        regionlist = Object.keys(regions);
        for (var i in regionlist)
        {
            countrylist = countrylist.concat(getcountriesinregion(regionlist[i]));
        }
    }
    else
    {
        if (region.isregion == 'Y')
        {
            regionlist = Object.keys(regions[name]);
            for (var i in regionlist)
            {
                countrylist = countrylist.concat(getcountriesinregion(regionlist[i]));
            }
        }
        else if (region.issubregion == 'Y')
        {
            return regions[region.region][name];
        }
        else if (region.iscountry == 'Y')
        {
            return regions[region.region][region.subregion];
        }
    }
    return countrylist;
}
