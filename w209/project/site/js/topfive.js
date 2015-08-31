function drawcharts(topfivedata, divid)
{	
	var noDecimals = d3.format(",.2f"),    // zero decimal places
	    rounding = function(val) { return Math.round(val/10000)/100;},
        format = function(d) { return noDecimals(rounding(d)) ; }; //+ "GkWh"
	
	
    var titlepadding = 65,
	    bottompadding = 5;
	var chartpadding = 10; //space between boxes of each top-5 category
	var barPadding = {y:20, x:20}; //y: vertical space between graph bars, x: offset from main box
	
	var width = 1400,
	    height = 370;
	// Margins for all bar-charts
    var margin = {top:0, right: 20, bottom: 20, left: 20};
    var w = width - margin.left - margin.right;
    var h = height - margin.top - margin.bottom - titlepadding - bottompadding;
	
    var NumCategories = topfivedata.length;
    var hgt = (h - (4 * barPadding.y))/(NumCategories + 1); // height of each bar
    
	var wid = (w - (NumCategories -1) * chartpadding)/NumCategories; // width of box
	var box_hgt = height - margin.top - margin.bottom ; // height of box

    // clear the canvas
    d3.select(divid).selectAll("*").remove();
    var svg = d3.select(divid)
		.append("svg")		   
		.attr("width", width)
		.attr("height", height)
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    for (var i = 0; i < topfivedata.length; i++)
    {
        chartdata = topfivedata[i];
        chart(chartdata, i);
    }
    
    function chart(cdata, ndx)
    {

    //create scale
    var scale = d3.scale.linear()
        .domain([0, cdata.maxvalue()])
        .range([0,wid - 2*barPadding.x]);
		
    /*var xAxis = d3.svg.axis()
		.scale(scale)
		.orient("bottom")
		.tickSize(box_hgt);  
	*/	
    //Left rectangles.  This is the horizontal bar that actually shows the metric			
    var bar =  svg.selectAll()
	    .data(cdata.countries)
	    .enter()
	    .append("g")
	    .attr("transform", "translate(" + (margin.left + (wid + chartpadding)*(ndx)) + "," + (margin.top + titlepadding) + ")");
    
	bar.append("rect")				   
	    .attr("y", function(d,i) { return margin.top + (hgt * i) + (barPadding.y * i);})
	    .attr("x", barPadding.x)
	    .attr("height", hgt)
	    .attr("width", function(d) { return scale(d.value);})			   
	    .attr("class","datarect")
            .on("click", function(d)
                {
                // if country or region update selection and update data
                var s = data[d.name];
                if (typeof s != 'undefined' && (s.isregion == 'Y' || s.issubregion == 'Y' || s.iscountry == 'Y'))
                {
                    document.getElementById("region").value = d.name;
                    if (s.iscountry == 'Y')
                    {
                        document.getElementById('hierarchy').value = 'region';
                    }
                    updatedata();
                }
                })
	    .append("title")
	    .text(function(d) { return d3.format("0,000")(d.value) + ' ' + d.units; });
		
	// Add text labels with bar value
        bar.append("text")
		.attr("y", function(d,i) { return margin.top + (hgt * i) + (barPadding.y * i) + hgt/2;})
		.attr("x", barPadding.x + 6)
		.attr("fill", "white")
		.attr("dy", ".35em")
	    .text(function(d, i) {
                if (d.units == 'MkWh') {
			if (i == 0) {
				return format(d.value) + " " + "Trillion kWh";
		        } else { return format(d.value); }
                } else {
                    if (i == 0) {
                        return d3.format(',.2f')(d.value / 1000) + " " + "Thousand kWh per capita";
                    } else { return d3.format(',.2f')(d.value / 1000); }
                }
            });
		
    // Add text labels with Country name
     bar.append("text")
	    .text(function(d) { return d.name })
	    .attr("y", function(d,i) { return margin.top + (hgt * i) + (barPadding.y * i) - (barPadding.y * .2);})
	    .attr("x", barPadding.x)
	    .attr("font-family", "sans-serif")
	    .attr("font-size", "12px")
	    .attr("text-anchor", "left")
	    .attr("class","yeartext")

	// Add title of top-5 category
	var title = svg.append("text")
	    .text(cdata.category)
		.attr("class","title")
	    .attr("y", margin.top + titlepadding/2 +5)
	//	.attr("x", margin.left + wid/2 + (ndx * (wid + chartpadding))) // Align in Center of Box
	//    .attr("text-anchor","middle");
		.attr("x", margin.left + barPadding.x + (ndx * (wid + chartpadding))) // Align at the Left
	    .attr("text-anchor","left");
		
		
        
    // Border that surrounds each top-5 chart
    var outline = svg.append("rect")			   
	    .attr("y", margin.top)
	    .attr("class", "outline")
	    .attr("x", margin.left + (ndx * (wid + chartpadding)))
	    .attr("width", wid )
	    .attr("height", box_hgt )
	    .attr("stroke", "#D8D8D8 ")
	    .attr("stroke-width", 2)
	    .attr("fill", "none")
	    //.attr("transform", "translate(" + ((wid + chartpadding) * ndx)+ ",0)");
    

        /*
        //axis
     var xAxis = d3.svg.axis()
	 .scale(scale)
	.orient("middle")
	.ticks(5);
        svg.append("g")
	.attr("class","axis")
	.attr("transform", "translate("+ ((wid+2*chartpadding)*(ndx)+margin.left) +"," + (h+margin.top+titlepadding+margin.bottom*.2)  + ")")
	.call(xAxis);
        */
    }
    
}
