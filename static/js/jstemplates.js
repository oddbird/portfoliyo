(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['ajax_error_msg'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var buffer = "", stack1, foundHelper, functionType="function", escapeExpression=this.escapeExpression;


  buffer += "<div class=\"";
  foundHelper = helpers.error_class;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.error_class; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\">\n  <p class=\"body\">\n    ";
  foundHelper = helpers.message;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.message; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\n    <a class=\"try-again\" href=\"#\">Try again</a> or reload the page.\n  </p>\n</div>\n";
  return buffer;});
templates['group_list'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers; partials = partials || Handlebars.partials;
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "\n<div class=\"additems\">\n  <a href=\"";
  foundHelper = helpers.add_group_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.add_group_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" class=\"additem-group ajax-link\">Add Group</a>\n\n  ";
  stack1 = depth0.add_students_bulk_url;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(2, program2, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n  ";
  stack1 = depth0.add_student_url;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(4, program4, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n</div>\n";
  return buffer;}
function program2(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "<a href=\"";
  foundHelper = helpers.add_students_bulk_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.add_students_bulk_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" class=\"action-addbulk ajax-link additem-village\">Signup Parents</a>";
  return buffer;}

function program4(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "or <a href=\"";
  foundHelper = helpers.add_student_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.add_student_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" class=\"action-addsingle ajax-link\">add a student by hand »</a>";
  return buffer;}

  buffer += "<ul class=\"itemlist\">\n  ";
  stack1 = depth0;
  stack1 = self.invokePartial(partials.group_list_items, 'group_list_items', stack1, helpers, partials);;
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n</ul>\n\n";
  stack1 = depth0.staff;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(1, program1, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;});
templates['group_list_items'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "\n<li class=\"listitem group\">\n  <a href=\"";
  foundHelper = helpers.group_uri;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_uri; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" class=\"group-link ajax-link listitem-select\" data-group-name=\"";
  foundHelper = helpers.name;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-id=\"";
  foundHelper = helpers.id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-students-url=\"";
  foundHelper = helpers.students_uri;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.students_uri; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-resource-url=\"";
  foundHelper = helpers.resource_uri;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.resource_uri; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-edit-url=\"";
  foundHelper = helpers.edit_uri;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.edit_uri; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-add-student-url=\"";
  foundHelper = helpers.add_student_uri;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.add_student_uri; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-add-students-bulk-url=\"";
  foundHelper = helpers.add_students_bulk_uri;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.add_students_bulk_uri; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-students=\"";
  stack1 = depth0.students;
  stack1 = helpers.each.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(2, program2, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\">\n    <span class=\"listitem-name\">";
  foundHelper = helpers.name;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "</span>\n    <span class=\"unread";
  stack1 = depth0.unread_count;
  stack1 = helpers.unless.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(4, program4, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\">\n      ";
  stack1 = depth0.unread_count;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.program(8, program8, data),fn:self.program(6, program6, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n    </span>\n  </a>\n</li>\n";
  return buffer;}
function program2(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  foundHelper = helpers.id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + " ";
  return buffer;}

function program4(depth0,data) {
  
  
  return " zero";}

function program6(depth0,data) {
  
  var stack1, foundHelper;
  foundHelper = helpers.unread_count;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.unread_count; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  return escapeExpression(stack1);}

function program8(depth0,data) {
  
  
  return "0";}

  stack1 = depth0.objects;
  stack1 = helpers.each.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(1, program1, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;});
templates['post_timeout_msg'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  


  return "<p class=\"timeout\">This message was not sent. You may have lost your connection to the internet. <a class=\"resend\" href=\"#\">Try again?</a> Or <a class=\"cancel\" href=\"#\">cancel this post</a>.</p>\n";});
templates['posts'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var buffer = "", stack1, self=this, functionType="function", escapeExpression=this.escapeExpression;

function program1(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "\n<article class=\"post ";
  stack1 = depth0.local;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.program(4, program4, data),fn:self.program(2, program2, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  stack1 = depth0.unread;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(11, program11, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\" data-author-id=\"";
  foundHelper = helpers.author_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.author_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-post-id=\"";
  foundHelper = helpers.post_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-author-sequence=\"";
  foundHelper = helpers.author_sequence_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.author_sequence_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-xhr-count=\"";
  foundHelper = helpers.xhr_count;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.xhr_count; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-mark-read-url=\"";
  foundHelper = helpers.mark_read_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.mark_read_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\">\n\n  <header class=\"post-meta\">\n    ";
  stack1 = depth0.local;
  stack1 = helpers.unless.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(13, program13, data)});
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
  stack1 = depth0.local;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.program(33, program33, data),fn:self.program(31, program31, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n  </p>\n\n</article>\n";
  return buffer;}
function program2(depth0,data) {
  
  
  return " local";}

function program4(depth0,data) {
  
  var buffer = "", stack1;
  stack1 = depth0.sms;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.program(7, program7, data),fn:self.program(5, program5, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  stack1 = depth0.unread;
  stack1 = helpers.unless.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(9, program9, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  return buffer;}
function program5(depth0,data) {
  
  
  return " sms";}

function program7(depth0,data) {
  
  
  return " no-sms";}

function program9(depth0,data) {
  
  
  return " old";}

function program11(depth0,data) {
  
  
  return " unread";}

function program13(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "\n    <div class=\"sms-info details\" title=\"";
  stack1 = depth0.from_sms;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.program(16, program16, data),fn:self.program(14, program14, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\">\n\n      <div class=\"details-body\" id=\"sms-post-";
  foundHelper = helpers.post_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "-details\">\n        ";
  stack1 = depth0.from_sms;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(21, program21, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n\n        ";
  stack1 = depth0.to_sms;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(23, program23, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n\n        ";
  stack1 = depth0.from_sms;
  stack1 = helpers.unless.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(26, program26, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n      </div>\n\n      <a href=\"#sms-post-";
  foundHelper = helpers.post_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "-details\" class=\"summary\">";
  stack1 = depth0.sms;
  stack1 = helpers.unless.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(29, program29, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "text messages sent/received</a>\n\n    </div>\n    ";
  return buffer;}
function program14(depth0,data) {
  
  
  return "Received by text.";}

function program16(depth0,data) {
  
  var buffer = "", stack1;
  stack1 = depth0.to_sms;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.program(19, program19, data),fn:self.program(17, program17, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += " sent.";
  return buffer;}
function program17(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "Text";
  foundHelper = helpers.plural_sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.plural_sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1);
  return buffer;}

function program19(depth0,data) {
  
  
  return "No texts";}

function program21(depth0,data) {
  
  
  return "Received by text. ";}

function program23(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "Text";
  foundHelper = helpers.plural_sms;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.plural_sms; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + " sent";
  stack1 = depth0.sms_recipients;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(24, program24, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += ".";
  return buffer;}
function program24(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += " to ";
  foundHelper = helpers.sms_recipients;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.sms_recipients; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1);
  return buffer;}

function program26(depth0,data) {
  
  var stack1;
  stack1 = depth0.to_sms;
  stack1 = helpers.unless.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(27, program27, data)});
  if(stack1 || stack1 === 0) { return stack1; }
  else { return ''; }}
function program27(depth0,data) {
  
  
  return "No text messages sent.";}

function program29(depth0,data) {
  
  
  return "no ";}

function program31(depth0,data) {
  
  var stack1, foundHelper;
  foundHelper = helpers.text;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.text; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  return escapeExpression(stack1);}

function program33(depth0,data) {
  
  var stack1, foundHelper;
  foundHelper = helpers.text;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.text; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  if(stack1 || stack1 === 0) { return stack1; }
  else { return ''; }}

  stack1 = depth0.posts;
  stack1 = helpers.each.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(1, program1, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;});
templates['student_list'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers; partials = partials || Handlebars.partials;
  var buffer = "", stack1, foundHelper, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n<div class=\"additems\">\n  ";
  stack1 = depth0.group_add_students_bulk_url;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(2, program2, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n  ";
  stack1 = depth0.group_add_student_url;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(4, program4, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n</div>\n";
  return buffer;}
function program2(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "<a href=\"";
  foundHelper = helpers.group_add_students_bulk_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_add_students_bulk_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" class=\"action-addbulk ajax-link additem-village\">Signup Parents</a>";
  return buffer;}

function program4(depth0,data) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "or <a href=\"";
  foundHelper = helpers.group_add_student_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_add_student_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" class=\"action-addsingle ajax-link\">add a student by hand »</a>";
  return buffer;}

  buffer += "<h2 class=\"listitem title grouptitle\">\n  <a href=\"#\" class=\"action-back groups\" title=\"Go back to group list\">Back</a>\n  <a href=\"";
  foundHelper = helpers.group_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" class=\"group-link ajax-link listitem-select\" data-group-name=\"";
  foundHelper = helpers.group_name;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_name; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-id=\"";
  foundHelper = helpers.group_id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-students-url=\"";
  foundHelper = helpers.group_students_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_students_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-resource-url=\"";
  foundHelper = helpers.group_resource_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_resource_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-edit-url=\"";
  foundHelper = helpers.group_edit_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_edit_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-add-student-url=\"";
  foundHelper = helpers.group_add_student_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_add_student_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-group-add-students-bulk-url=\"";
  foundHelper = helpers.group_add_students_bulk_url;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_add_students_bulk_url; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-removed=\"";
  foundHelper = helpers.removed;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.removed; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\">\n    <span class=\"listitem-name\">";
  foundHelper = helpers.group_name;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.group_name; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "</span>\n  </a>\n</h2>\n\n<ul class=\"itemlist\">\n  ";
  stack1 = depth0;
  stack1 = self.invokePartial(partials.student_list_items, 'student_list_items', stack1, helpers, partials);;
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n</ul>\n\n";
  stack1 = depth0.staff;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(1, program1, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;});
templates['student_list_items'] = template(function (Handlebars,depth0,helpers,partials,data) {
  helpers = helpers || Handlebars.helpers;
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data,depth1) {
  
  var buffer = "", stack1, foundHelper;
  buffer += "\n<li class=\"listitem student\">\n  <a href=\"";
  foundHelper = helpers.village_uri;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.village_uri; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1);
  stack1 = depth1.all_students;
  stack1 = helpers.unless.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.programWithDepth(program2, data, depth1)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\" class=\"ajax-link listitem-select\" data-id=\"";
  foundHelper = helpers.id;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.id; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\" data-name=\"";
  foundHelper = helpers.name;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "\">\n    <span class=\"listitem-name\">";
  foundHelper = helpers.name;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  buffer += escapeExpression(stack1) + "</span>\n    <span class=\"unread";
  stack1 = depth0.unread_count;
  stack1 = helpers.unless.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.program(4, program4, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\">\n      ";
  stack1 = depth0.unread_count;
  stack1 = helpers['if'].call(depth0, stack1, {hash:{},inverse:self.program(8, program8, data),fn:self.program(6, program6, data)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n    </span>\n  </a>\n</li>\n";
  return buffer;}
function program2(depth0,data,depth2) {
  
  var buffer = "", stack1;
  buffer += "?group=";
  stack1 = depth2.group_id;
  stack1 = typeof stack1 === functionType ? stack1() : stack1;
  buffer += escapeExpression(stack1);
  return buffer;}

function program4(depth0,data) {
  
  
  return " zero";}

function program6(depth0,data) {
  
  var stack1, foundHelper;
  foundHelper = helpers.unread_count;
  if (foundHelper) { stack1 = foundHelper.call(depth0, {hash:{}}); }
  else { stack1 = depth0.unread_count; stack1 = typeof stack1 === functionType ? stack1() : stack1; }
  return escapeExpression(stack1);}

function program8(depth0,data) {
  
  
  return "0";}

  stack1 = depth0.objects;
  stack1 = helpers.each.call(depth0, stack1, {hash:{},inverse:self.noop,fn:self.programWithDepth(program1, data, depth0)});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;});
})();