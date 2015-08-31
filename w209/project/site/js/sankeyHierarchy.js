d3.sankeyHierarchy = function() {
    var sankeyHierarchy = {},
        nodeWidth = 24,
        globalHeight = 100,
        globalWidth = 100,
        layoutDetails = [],
        leftToRight = true,
        flatNodesList = [],
        yCoordinateTracker = [],
        yParentCoordinateTracker = [],
        paths = [], 
        heightPadding = 40, 
        heightAfterPadding = 0;

	  

  sankeyHierarchy.nodeWidth = function(_) {
    if (!arguments.length) return nodeWidth;
    nodeWidth = +_;
    return sankeyHierarchy;
  };

  sankeyHierarchy.flatNodesList = function (_) {
      if (!arguments.length) return flatNodesList;
      flatNodesList = _;
      return sankeyHierarchy;
  };

  sankeyHierarchy.paths = function (_) {
      if (!arguments.length) return paths;
      paths = _;
      return sankeyHierarchy;
  };

  sankeyHierarchy.nodes = function(_) {
    if (!arguments.length) return nodes;
    nodes = _;
    return sankeyHierarchy;
  };

  sankeyHierarchy.globalHeight = function(_) {
    if (!arguments.length) return globalHeight;
    globalHeight = _;
    heightAfterPadding = globalHeight - heightPadding;
    return sankeyHierarchy;
  };

  sankeyHierarchy.globalWidth = function(_) {
      if (!arguments.length) return globalWidth;
      globalWidth = _;
    return sankeyHierarchy;
  };

  sankeyHierarchy.layoutDetails = function(_) {
    if (!arguments.length) return layoutDetails;
    layoutDetails = _;
    //yCoordinateTracker = _.length;
    yCoordinateTracker = Array.apply(null, Array(_.length)).map(Number.prototype.valueOf, 0);
    yParentCoordinateTracker = Array.apply(null, Array(_.length)).map(Number.prototype.valueOf, 0);

    return sankeyHierarchy;
  };

  sankeyHierarchy.leftToRight = function(_) {
    if (!arguments.length) return leftToRight;
    leftToRight = _;
    return sankeyHierarchy;
  };
  
  sankeyHierarchy.generateCoords = function () {	  
      setupNodes(nodes, 0, 0);
  };
  
  
  function setupNodes(thisNodes, level, parentColor, parentX, parentY1, parentY2, parentName,parentPercentage) {

      //find top coordinate and bottom coordinate
      heightAtLevel = layoutDetails[level].height;

      if (heightAtLevel == "max")
          heightAtLevel = heightAfterPadding

      //padding at this level
      paddingAtLevel = layoutDetails[level].padding;

      var initialY = heightAfterPadding / 2 - heightAtLevel / 2
      //start at the topmost position
      if (yCoordinateTracker[level] == 0) {
          yCoordinateTracker[level] = initialY;
      } else {
          initialY = yCoordinateTracker[level];
      }

      //for each node, generage x and y coordinates	
      index = 0;
      nodelength = thisNodes.length;

      var childrenStartingY = 0;

      var startingX = globalWidth - nodeWidth - (globalWidth * layoutDetails[level].widthPercentage / 100);
      if (layoutDetails[level].widthPercentage == 100) {//if leftmost, correct for nodeWidth
          startingX += nodeWidth ;
      }

      for (var i = 0; i < thisNodes.length; i++) {
          node = thisNodes[i];
          //thisNodes.forEach(function(node) {
          var topPadding, bottomPadding = paddingAtLevel / 2;
          if (index == 0) //is top element
          {
              topPadding = 0
          }
          else if (index == (nodelength - 1)) //if it is first node or last node, no padding is required 
          {
              bottomPadding = 0;
          }

          node.x = startingX;

          node.y = yCoordinateTracker[level];

          var heightHere = layoutDetails[level].height;
          if (heightHere == "max")
              heightHere = heightAfterPadding;

          var rectHeight = heightHere * (node.percent / 100);
          node.dy = rectHeight;

          node.color = color(node.name.replace(/ .*/, ""));
          yCoordinateTracker[level] += bottomPadding + rectHeight;
          flatNodesList.push(node);

          if (node.children.length != 0) {
              //keep updating starting height
              setupNodes(node.children, level + 1, node.color, node.x, node.y, node.dy, node.name, node.percent);
          }

          for (currentLevel = level+1; currentLevel < yCoordinateTracker.length; currentLevel++)
          {
              yCoordinateTracker[currentLevel] = yCoordinateTracker[currentLevel] + layoutDetails[level].childPadding;
          }
          //});
      }
      if (level != 0) {

         curvature = .5;

         var xi = d3.interpolateNumber((startingX + nodeWidth), parentX),
            x2 = xi(curvature),
            x3 = xi(1 - curvature);

          var bxi = d3.interpolateNumber(parentX, (startingX + nodeWidth)),
            bx2 = bxi(curvature),
            bx3 = bxi(1 - curvature);

          //d: "M" + (startingX + nodeWidth) + " " + initialY + " L " + parentX + " " + parentY1 + " V " + (parentY1 + parentY2) + " L " + (startingX + nodeWidth) + " " + yCoordinateTracker[level] + "  Z",
          //d: "M" + (startingX + nodeWidth) + "," + initialY + " C " + x2 + "," + initialY + " " + x3 + "," + parentY1 + " " + parentX + "," + parentY1 + " V " + (parentY1 + parentY2) + " L " + (startingX + nodeWidth) + " " + yCoordinateTracker[level] + "  Z",

          paths.push({
              d: "M" + (startingX + nodeWidth) + "," + initialY + " C " + x2 + "," + initialY + " " + x3 + "," + parentY1 + " " + parentX + "," + parentY1 + " V " + (parentY1 + parentY2)
                  + " C " + bx2 + "," + (parentY1 + parentY2) + " " + bx3 + "," + yCoordinateTracker[level]  + " " + (startingX + nodeWidth) + "," + yCoordinateTracker[level] +  " Z",
              color: parentColor,
			  name: parentName,
			  percent:parentPercentage
          });
      }

  }


  sankeyHierarchy.relayout = function() {
    computeLinkDepths();
    return sankeyHierarchy;
  };

  sankeyHierarchy.link = function() {
    var curvature = .5;

    function link(d) {
      var x0 = d.source.x + d.source.dx,
          x1 = d.target.x,
          xi = d3.interpolateNumber(x0, x1),
          x2 = xi(curvature),
          x3 = xi(1 - curvature),
          y0 = d.source.y + d.sy + d.dy / 2,
          y1 = d.target.y + d.ty + d.dy / 2;
      return "M" + x0 + "," + y0
           + "C" + x2 + "," + y0
           + " " + x3 + "," + y1
           + " " + x1 + "," + y1;
    }

    link.curvature = function(_) {
      if (!arguments.length) return curvature;
      curvature = +_;
      return link;
    };

    return link;
  };








  return sankeyHierarchy;
};
