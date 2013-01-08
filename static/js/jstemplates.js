(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['active_item_removed_msg'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var buffer = "", stack1, foundHelper, functionType="function", escapeExpression=this.escapeExpression;


  buffer += "<li class=\"message warning\">\n  <p>\n    The ";
  foundHelper = helpers.item;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.item; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + " you are viewing has been removed. Any further changes will be lost. Please <a href=\"/\">reload your page</a>.\n  </p>\n  <a href=\"#\" class=\"close\">dismiss this message</a>\n</li>\n";
  return buffer;});
})();