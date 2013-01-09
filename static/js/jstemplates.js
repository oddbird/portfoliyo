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
templates['post'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var buffer = "", stack1, foundHelper, self=this, functionType="function", blockHelperMissing=helpers.blockHelperMissing, escapeExpression=this.escapeExpression;

function program1(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "\n<article class=\"post ";
  foundHelper = helpers.local;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.program(2, program2, data),fn:self.noop}); }
  else { stack1 = depth0.local; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.local) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.program(2, program2, data),fn:self.noop}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  foundHelper = helpers.unread;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(9, program9, data)}); }
  else { stack1 = depth0.unread; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.unread) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(9, program9, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  foundHelper = helpers.local;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(11, program11, data)}); }
  else { stack1 = depth0.local; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.local) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(11, program11, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\" data-author-id=\"";
  foundHelper = helpers.author_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.author_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\"";
  foundHelper = helpers.post_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(13, program13, data)}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.post_id) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(13, program13, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  foundHelper = helpers.author_sequence_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(15, program15, data)}); }
  else { stack1 = depth0.author_sequence_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.author_sequence_id) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(15, program15, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  foundHelper = helpers.xhr_count;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(17, program17, data)}); }
  else { stack1 = depth0.xhr_count; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.xhr_count) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(17, program17, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  foundHelper = helpers.mark_read_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(19, program19, data)}); }
  else { stack1 = depth0.mark_read_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.mark_read_url) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(19, program19, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += ">\n\n  <header class=\"post-meta\">\n    ";
  foundHelper = helpers.local;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.program(21, program21, data),fn:self.noop}); }
  else { stack1 = depth0.local; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.local) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.program(21, program21, data),fn:self.noop}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n    <h3 class=\"byline vcard\">\n      <b class=\"title\">";
  foundHelper = helpers.role;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.role; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + ":</b>\n      <span class=\"fn\">";
  foundHelper = helpers.author;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.author; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "</span>\n    </h3>\n    <time class=\"pubdate\" datetime=\"";
  foundHelper = helpers.timestamp;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.timestamp; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\">";
  foundHelper = helpers.date;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.date; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + " at ";
  foundHelper = helpers.time;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.time; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "</time>\n  </header>\n\n  <p class=\"post-text\">\n    ";
  foundHelper = helpers.local;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(37, program37, data)}); }
  else { stack1 = depth0.local; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.local) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(37, program37, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  foundHelper = helpers.local;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.program(39, program39, data),fn:self.noop}); }
  else { stack1 = depth0.local; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.local) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.program(39, program39, data),fn:self.noop}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n  </p>\n\n</article>\n";
  return buffer;}
function program2(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  foundHelper = helpers.sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(3, program3, data)}); }
  else { stack1 = depth0.sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.sms) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(3, program3, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  foundHelper = helpers.sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.program(5, program5, data),fn:self.noop}); }
  else { stack1 = depth0.sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.sms) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.program(5, program5, data),fn:self.noop}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  foundHelper = helpers.unread;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.program(7, program7, data),fn:self.noop}); }
  else { stack1 = depth0.unread; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.unread) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.program(7, program7, data),fn:self.noop}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  return buffer;}
function program3(depth0,data) {
  
  
  return " sms";}

function program5(depth0,data) {
  
  
  return " no-sms";}

function program7(depth0,data) {
  
  
  return " old";}

function program9(depth0,data) {
  
  
  return " unread";}

function program11(depth0,data) {
  
  
  return " local";}

function program13(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += " data-post-id=\"";
  foundHelper = helpers.post_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\"";
  return buffer;}

function program15(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += " data-author-sequence=\"";
  foundHelper = helpers.author_sequence_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.author_sequence_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\"";
  return buffer;}

function program17(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += " data-xhr-count=\"";
  foundHelper = helpers.xhr_count;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.xhr_count; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\"";
  return buffer;}

function program19(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += " data-mark-read-url=\"";
  foundHelper = helpers.mark_read_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.mark_read_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\"";
  return buffer;}

function program21(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "\n    <div class=\"sms-info details\" title=\"";
  foundHelper = helpers.from_sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(22, program22, data)}); }
  else { stack1 = depth0.from_sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.from_sms) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(22, program22, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  foundHelper = helpers.to_sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.program(24, program24, data),fn:self.noop}); }
  else { stack1 = depth0.to_sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.to_sms) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.program(24, program24, data),fn:self.noop}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  foundHelper = helpers.to_sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(26, program26, data)}); }
  else { stack1 = depth0.to_sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.to_sms) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(26, program26, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += " sent.\">\n\n      <div class=\"details-body\" id=\"sms-post-";
  foundHelper = helpers.post_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "-details\">\n        ";
  foundHelper = helpers.from_sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(28, program28, data)}); }
  else { stack1 = depth0.from_sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.from_sms) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(28, program28, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n\n        ";
  foundHelper = helpers.to_sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(30, program30, data)}); }
  else { stack1 = depth0.to_sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.to_sms) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(30, program30, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n\n        ";
  foundHelper = helpers.to_sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.program(33, program33, data),fn:self.noop}); }
  else { stack1 = depth0.to_sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.to_sms) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.program(33, program33, data),fn:self.noop}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n      </div>\n\n      <a href=\"#sms-post-";
  foundHelper = helpers.post_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "-details\" class=\"summary\">";
  foundHelper = helpers.sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.program(35, program35, data),fn:self.noop}); }
  else { stack1 = depth0.sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.sms) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.program(35, program35, data),fn:self.noop}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "text messages sent</a>\n\n    </div>\n    ";
  return buffer;}
function program22(depth0,data) {
  
  
  return "Received by text. ";}

function program24(depth0,data) {
  
  
  return " No texts ";}

function program26(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += " Text";
  foundHelper = helpers.plural_sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.plural_sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + " ";
  return buffer;}

function program28(depth0,data) {
  
  
  return " Received by text. ";}

function program30(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "\n        Text";
  foundHelper = helpers.plural_sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.plural_sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + " sent ";
  foundHelper = helpers.sms_recipients;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(31, program31, data)}); }
  else { stack1 = depth0.sms_recipients; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.sms_recipients) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(31, program31, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += ".\n        ";
  return buffer;}
function program31(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += " to ";
  foundHelper = helpers.sms_recipients;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.sms_recipients; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1);
  return buffer;}

function program33(depth0,data) {
  
  
  return "\n        No text messages sent.\n        ";}

function program35(depth0,data) {
  
  
  return "no ";}

function program37(depth0,data) {
  
  var stack1, foundHelper;
  foundHelper = helpers.text;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.text; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  return escapeExpression(stack1);}

function program39(depth0,data) {
  
  var stack1, foundHelper;
  foundHelper = helpers.text;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.text; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if(stack1 || stack1 === 0) { return stack1; }
  else { return ''; }}

  foundHelper = helpers.posts;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{},inverse:self.noop,fn:self.program(1, program1, data)}); }
  else { stack1 = depth0.posts; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if (!helpers.posts) { stack1 = blockHelperMissing.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(1, program1, data)}); }
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;});
templates['post_timeout_msg'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  


  return "<p class=\"timeout\">This message was not sent. You may have lost your connection to the internet. <a class=\"resend\" href=\"#\">Try again?</a> Or <a class=\"cancel\" href=\"#\">cancel this post</a>.</p>\n";});
templates['remove_listitem'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var buffer = "", stack1, foundHelper, functionType="function", escapeExpression=this.escapeExpression;


  buffer += "<span class=\"listitem-select removed\">\n  ";
  foundHelper = helpers.name;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\n</span>\n\n<div class=\"listitem-actions\">\n  <button class=\"undo-action-remove\" title=\"undo removal\">undo removal</button>\n</div>\n";
  return buffer;});
})();