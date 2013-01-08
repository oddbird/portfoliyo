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
templates['ajax_403_msg'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  


  return "<li class=\"message error\">\n  <p>\n    Sorry, you don't have permission to access this page. Please <a href=\"/login/\">log in</a> with an account that does or visit a different page.\n  </p>\n  <a href=\"#\" class=\"close\">dismiss this message</a>\n</li>\n";});
templates['ajax_error_msg'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var buffer = "", stack1, foundHelper, functionType="function", escapeExpression=this.escapeExpression;


  buffer += "<div class=\"";
  foundHelper = helpers.error_class;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.error_class; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\">\n  <p>\n    ";
  foundHelper = helpers.message;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.message; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\n    <a class=\"try-again\" href=\"#\">Try again</a> or reload the page.\n  </p>\n</div>\n";
  return buffer;});
templates['flash_warning_msg'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  


  return "<li class=\"message warning\">\n  <p>\n    This site requires Flash Player version 10.0.0 or higher to display live updates. Refresh your browser page to see new posts, or <a href=\"http://get.adobe.com/flashplayer/\" target=\"_blank\">download Flash Player</a>.\n  </p>\n  <a href=\"#\" class=\"close\">dismiss this message</a>\n</li>\n";});
templates['post_timeout_msg'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  


  return "<p class=\"timeout\">This message was not sent. You may have lost your connection to the internet. <a class=\"resend\" href=\"#\">Try again?</a> Or <a class=\"cancel\" href=\"#\">cancel this post</a>.</p>\n";});
})();