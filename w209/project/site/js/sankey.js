d3.sankey = function() {
  var sankey = {},
      nodeWidth = 24,
      nodePadding = 8,
      size = [1, 1],
      nodes = [],
      links = [],
	  scaleRight = false,
	  rightHeight = 1, // Scale right-most nodes to this height (for production side)
	  scaleLeft = false,  
	  leftHeight = 1;  // Scale left-most nodes to this height (for consumption side)
 
  sankey.nodeWidth = function(_) {
    if (!arguments.length) return nodeWidth;
    nodeWidth = +_;
    return sankey;
  };
  
  sankey.scaleRight = function(_) {
    if (!arguments.length) return scaleRight;
    scaleRight = _;
    return sankey;
  };

  sankey.scaleLeft = function(_) {
    if (!arguments.length) return scaleLeft;
    scaleLeft = _;
    return sankey;
  };
  
  sankey.rightHeight = function(_) {
    if (!arguments.length) return size[1];
    rightHeight = +_;
    return sankey;
  };
  
  sankey.leftHeight = function(_) {
    if (!arguments.length) return size[1];
    leftHeight = +_;
    return sankey;
  };
 
  sankey.nodePadding = function(_) {
    if (!arguments.length) return nodePadding;
    nodePadding = +_;
    return sankey;
  };
 
  sankey.nodes = function(_) {
    if (!arguments.length) return nodes;
    nodes = _;
    return sankey;
  };
 
  sankey.links = function(_) {
    if (!arguments.length) return links;
    links = _;
    return sankey;
  };
 
  sankey.size = function(_) {
    if (!arguments.length) return size;
    size = _;
    return sankey;
  };
 
  sankey.layout = function(iterations) {
    computeNodeLinks();               // For each node, incoming and outgoing links
    computeNodeValues();              // Height of each node stored as value 
	computeNodeBreadths();            // Breadth -> placement of nodes along x-axis
    computeNodeDepths(iterations);    // Depth   -> placement of nodes along y-axis
    computeLinkDepths();              // 
	//Added
	if (scaleRight) {
		reScaleRightNodes();
	}
	if (scaleLeft) {
		reScaleLeftNodes();
	}
	
    return sankey;
  };
 
  sankey.relayout = function() {
    computeLinkDepths();
    return sankey;
  };
 
  sankey.link = function() {
    var curvature = .5;
 
    /* //Original Curve
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
	/* */
	function link(d) {
	/* Draw path from top of source to top of target,
	     go down vertically to bottom of target,
		 and then go from bottom of target to bottom of source
		 Coordinates are:
		 Top Source: 	(x0,y0)
		 Bottom Source: (x1,y1)
		 Top Target: 	(x1,y4)
		 Bottom Target: (x0,y5)
		All other coordinates are control points to create smooth curves
	*/ 
	  var x0 = d.source.x + d.source.dx,
          x1 = d.target.x,
          xi = d3.interpolateNumber(x0, x1),
          x2 = xi(curvature),
          x3 = xi(1 - curvature),
          y0 = d.source.y + d.sy,
		  y5 = d.source.y + d.sy + d.dy,
          y1 = d.target.y + d.ty,
		  y4 = d.target.y + d.ty + d.tdy;

      return "M" + x0 + "," + y0
           + "C" + x2 + "," + y0
           + " " + x3 + "," + y1
           + " " + x1 + "," + y1
		   + "V" + x1 + "," + y4
		   + "C" + x3 + "," + y4
           + " " + x2 + "," + y5
           + " " + x0 + "," + y5
		   + "Z" ;
    } 
 
    link.curvature = function(_) {
      if (!arguments.length) return curvature;
      curvature = +_;
      return link;
    };
 
    return link;
  };
 
  // Populate the sourceLinks and targetLinks for each node.
  // Also, if the source and target are not objects, assume they are indices.
  function computeNodeLinks() {
    nodes.forEach(function(node) {
      node.sourceLinks = [];
      node.targetLinks = [];
    });
    links.forEach(function(link) {
      var source = link.source,
          target = link.target;
      if (typeof source === "number") source = link.source = nodes[link.source];
      if (typeof target === "number") target = link.target = nodes[link.target];
      source.sourceLinks.push(link);
      target.targetLinks.push(link);
    });
  }
 
  // Compute the value (size) of each node by summing the associated links.
  function computeNodeValues() {
    nodes.forEach(function(node) {
	  
      node.value = Math.max(
        d3.sum(node.sourceLinks, value),
        d3.sum(node.targetLinks, value)
      );
    });
  }
 
  // Iteratively assign the breadth (x-position) for each node.
  // Nodes are assigned the maximum breadth of incoming neighbors plus one;
  // nodes with no incoming links are assigned breadth zero, while
  // nodes with no outgoing links are assigned the maximum breadth.
  function computeNodeBreadths() {
    var remainingNodes = nodes,
        nextNodes,
		rightmostNodes,
        x = 0;
	
	// Determine the "column" or x-position that the node should be at based on an arbitrary scale
    while (remainingNodes.length) {
      nextNodes = [];
      remainingNodes.forEach(function(node) {
		node.x = x;
        node.dx = nodeWidth;
        node.sourceLinks.forEach(function(link) {
          nextNodes.push(link.target);
        });
      });
      remainingNodes = nextNodes;
      ++x;
    }
	
	if (scaleRight) {
		moveSinksRight(x);
		moveSourcesRight();
	}
	if (scaleLeft) {
		tagSourcesLeft();
	}
	
	// x-position from arbitrary scale to actual scale (based on width)
    scaleNodeBreadths((size[0] - nodeWidth) / (x - 1));
  }
  
  function moveSourcesRight() {
    nodes.forEach(function(node) {
      if (!node.targetLinks.length) {
        node.x = d3.min(node.sourceLinks, function(d) { return d.target.x; }) - 1;
      }
    });
  }
 
  function moveSinksRight(x) {
    nodes.forEach(function(node) {
      if (!node.sourceLinks.length) {
        node.x = x - 1;
		node.right_ghost = 1;
      }
    });
  }
  
  function tagSourcesLeft() {
    nodes.forEach(function(node) {
      if (!node.targetLinks.length) {
		node.left_ghost = 1;
      }
    });
  }
  
  function scaleNodeBreadths(kx) {
    nodes.forEach(function(node) {
      node.x *= kx;
    });
  }
 
  function computeNodeDepths(iterations) {
    var nodesByBreadth = d3.nest()
        .key(function(d) { return d.x; })
        .sortKeys(d3.ascending)
        .entries(nodes)
        .map(function(d) { return d.values; });
 
    //
    initializeNodeDepth();
    resolveCollisions();
    for (var alpha = 1; iterations > 0; --iterations) {
      relaxRightToLeft(alpha *= .99);
      resolveCollisions();
      relaxLeftToRight(alpha);
      resolveCollisions();
    }
 
    function initializeNodeDepth() {
      var ky = d3.min(nodesByBreadth, function(nodes) {
        return (size[1] - (nodes.length - 1) * nodePadding) / d3.sum(nodes, value);
      });
 
      nodesByBreadth.forEach(function(nodes) {
        nodes.forEach(function(node, i) {
          node.y = i;
          node.dy = node.value * ky;
        });
      });
 
      links.forEach(function(link) {
        link.dy = link.value * ky;
		link.tdy = link.dy;  	// Keep dy for source and create tdy for target dy
      });
    }
 
    function relaxLeftToRight(alpha) {
      nodesByBreadth.forEach(function(nodes, breadth) {
        nodes.forEach(function(node) {
          if (node.targetLinks.length) {
            var y = d3.sum(node.targetLinks, weightedSource) / d3.sum(node.targetLinks, value);
            node.y += (y - center(node)) * alpha;
          }
        });
      });
 
      function weightedSource(link) {
        return center(link.source) * link.value;
      }
    }
 
    function relaxRightToLeft(alpha) {
      nodesByBreadth.slice().reverse().forEach(function(nodes) {
        nodes.forEach(function(node) {
          if (node.sourceLinks.length) {
            var y = d3.sum(node.sourceLinks, weightedTarget) / d3.sum(node.sourceLinks, value);
            node.y += (y - center(node)) * alpha;
          }
        });
      });
 
      function weightedTarget(link) {
        return center(link.target) * link.value;
      }
    }
 
    function resolveCollisions() {
      nodesByBreadth.forEach(function(nodes) {
        var node,
            dy,
            y0 = 0,
            n = nodes.length,
            i;
 
        // Push any overlapping nodes down.
        nodes.sort(ascendingDepth);
        for (i = 0; i < n; ++i) {
          node = nodes[i];
          dy = y0 - node.y;
          if (dy > 0) node.y += dy;
          y0 = node.y + node.dy + nodePadding;
        }
 
        // If the bottommost node goes outside the bounds, push it back up.
        dy = y0 - nodePadding - size[1];
        if (dy > 0) {
          y0 = node.y -= dy;
 
          // Push any overlapping nodes back up.
          for (i = n - 2; i >= 0; --i) {
            node = nodes[i];
            dy = node.y + node.dy + nodePadding - y0;
            if (dy > 0) node.y -= dy;
            y0 = node.y;
          }
        }
      });
    }
 
    function ascendingDepth(a, b) {
      return a.y - b.y;
    }
  }
 
  function computeLinkDepths() {
    nodes.forEach(function(node) {
      node.sourceLinks.sort(ascendingTargetDepth);
      node.targetLinks.sort(ascendingSourceDepth);
    });
    nodes.forEach(function(node) {
      var sy = 0, ty = 0;
      node.sourceLinks.forEach(function(link) {
        link.sy = sy;
        sy += link.dy;
      });
      node.targetLinks.forEach(function(link) {
        link.ty = ty;
        ty += link.dy;
      });
    });
 
    function ascendingSourceDepth(a, b) {
      return a.source.y - b.source.y;
    }
 
    function ascendingTargetDepth(a, b) {
      return a.target.y - b.target.y;
    }
  }
 
  function center(node) {
    return node.y + node.dy / 2;
  }
 
  function value(link) {
    return link.value;
  }
 
   // --- Added Functions --------------------------------------
  function reScaleRightNodes() {
	var yStart = (size[1] - rightHeight) /2,
		yRescaleAbs = d3.scale.linear()
						   .domain([0,size[1]])
						   .range([yStart, yStart + rightHeight]); 
		yRescaleRel = d3.scale.linear()
						   .domain([0,size[1]])
						   .range([0, rightHeight]); 
						   
	nodes.forEach(function(node) {
      if (node.right_ghost == 1) {
        node.x = node.x + node.dx;
		node.dx = 0;
        node.value = yRescaleAbs(node.value);
		node.y = yRescaleAbs(node.y);
        node.dy = yRescaleRel(node.dy);
		node.targetLinks.forEach(function(link) {
			link.ty = yRescaleRel(link.ty);
			link.tdy = yRescaleRel(link.tdy);
		});
      }
    });
  }
  function reScaleLeftNodes() {
	var yStart = (size[1] - leftHeight) /2,
		yRescaleAbs = d3.scale.linear()
						   .domain([0,size[1]])
						   .range([yStart, yStart + leftHeight]); 
		yRescaleRel = d3.scale.linear()
						   .domain([0,size[1]])
						   .range([0, leftHeight]); 
						   
	nodes.forEach(function(node) {
      if (node.left_ghost == 1) {
		node.dx = 0;
        node.value = yRescaleAbs(node.value);
		node.y = yRescaleAbs(node.y);
        node.dy = yRescaleRel(node.dy);
		node.sourceLinks.forEach(function(link) {
			link.sy = yRescaleRel(link.sy);
			link.dy = yRescaleRel(link.dy);
		});
      }
    });
  }
  
  return sankey;
}