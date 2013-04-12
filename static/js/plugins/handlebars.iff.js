//	Handlebars Equality helper.
//	{{#iff one}}:  !!one
//	{{#iff one two}}:  one === two
//	{{#iff one "[operator]" two}}:  one [operator] two
Handlebars.registerHelper('iff', function(){
	var args = Array.prototype.slice.call(arguments);

	var	left = args[0],
		operator = '===',
		right,
		options = {};

	if(args.length === 2){
		right = true;
		options = args[1];
	}

	if(args.length === 3){
		right = args[1];
		options = args[2];
	}

	if(args.length === 4){
		operator = args[1];
		right = args[2];
		options = args[3];
	}

	if(options.hash && options.hash['case'] === false){
		left = (''+left).toLowerCase();
		right = (''+right).toLowerCase();
	}

	var operators = {
		"^==$": function(l, r){ return l == r; },
		"^!=$": function(l, r){ return l !== r; },
		"^IS$|^===$": function(l, r){ return l === r; },
		"^NOT$|^IS NOT$|^!==$|^!$": function(l, r){ return l != r; },
		"^OR$|^\\|\\|$": function(l, r){ return l || r; },
		"^AND$|^&&$": function(l, r){ return l && r; },
		"^MOD$|^%$": function(l, r){ return !(l % r); },
		"^<$": function(l, r){ return l < r; },
		"^>$": function(l, r){ return l > r; },
		"^<=$": function(l, r){ return l <= r; },
		"^>=$": function(l, r){ return l >= r; },
		"^typeof$": function(l, r){ return typeof l == r; },
		"^IN$|^E$": function(l, r){
			var isPresent = false;
			if(typeof r === 'object'){
				if(r.indexOf && r instanceof Array){
					if(/^\d+$/.test(l)){
						isPresent = !!~r.indexOf(+l) || !!~r.indexOf(''+l);
					}
					return isPresent || !!~r.indexOf(l);
				}else{
					return l in r;
				}
			}
		}
	};

	var op, result, expression;
	for(op in operators){
		expression = RegExp(op, 'i');

		if(expression.test(operator)){
			result = operators[op](left, right);

			if(result){
				return options.fn(this);
			}else{
				return options.inverse(this);
			}
		}
	}

	if(!operators[operator]){
		throw new Error("Handlerbars Helper 'compare' doesn't know the operator " + operator);
	}
});
