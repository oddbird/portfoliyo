this["PYO"] = this["PYO"] || {};
this["PYO"]["templates"] = this["PYO"]["templates"] || {};

this["PYO"]["templates"]["ajax_error_msg"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression;


  buffer += "<div class=\"";
  if (stack1 = helpers.error_class) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.error_class; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">\n  <p class=\"body\">\n    ";
  if (stack1 = helpers.message) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.message; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\n    <a class=\"try-again\" href=\"#\">Try again</a> or reload the page.\n  </p>\n</div>\n";
  return buffer;
  });

this["PYO"]["templates"]["group_list"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; partials = partials || Handlebars.partials; data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n<div class=\"additems\">\n  <a href=\"";
  if (stack1 = helpers.add_group_url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.add_group_url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" class=\"additem-group ajax-link\">Add Group</a>\n\n  ";
  stack1 = helpers['if'].call(depth0, depth0.add_student_url, {hash:{},inverse:self.noop,fn:self.program(2, program2, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n</div>\n";
  return buffer;
  }
function program2(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "<a href=\"";
  if (stack1 = helpers.add_student_url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.add_student_url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" class=\"ajax-link additem-village\">Signup Parents</a>";
  return buffer;
  }

  buffer += "<div class=\"navtitle\">\n  <h2 class=\"groups-title\">All Groups</h2>\n</div>\n\n<ul class=\"itemlist groups-list\">\n  ";
  stack1 = self.invokePartial(partials.group_list_items, 'group_list_items', depth0, helpers, partials, data);
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n</ul>\n\n";
  stack1 = helpers['if'].call(depth0, depth0.staff, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  });

this["PYO"]["templates"]["group_list_items"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n<li class=\"listitem group\">\n  <a href=\"";
  if (stack1 = helpers.group_uri) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_uri; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" class=\"group-link ajax-link listitem-select\" data-group-name=\"";
  if (stack1 = helpers.name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-id=\"";
  if (stack1 = helpers.id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-students-url=\"";
  if (stack1 = helpers.students_uri) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.students_uri; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-resource-url=\"";
  if (stack1 = helpers.resource_uri) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.resource_uri; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-edit-url=\"";
  if (stack1 = helpers.edit_uri) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.edit_uri; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-add-student-url=\"";
  if (stack1 = helpers.add_student_uri) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.add_student_uri; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-add-students-bulk-url=\"";
  if (stack1 = helpers.add_students_bulk_uri) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.add_students_bulk_uri; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-students=\"";
  stack1 = helpers.each.call(depth0, depth0.students, {hash:{},inverse:self.noop,fn:self.program(2, program2, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\">\n    <span class=\"listitem-name\">";
  if (stack1 = helpers.name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</span>\n    <span class=\"unread";
  stack1 = helpers.unless.call(depth0, depth0.unread_count, {hash:{},inverse:self.noop,fn:self.program(4, program4, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\">\n      ";
  stack1 = helpers['if'].call(depth0, depth0.unread_count, {hash:{},inverse:self.program(8, program8, data),fn:self.program(6, program6, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n    </span>\n  </a>\n</li>\n";
  return buffer;
  }
function program2(depth0,data) {
  
  var buffer = "", stack1;
  if (stack1 = helpers.id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + " ";
  return buffer;
  }

function program4(depth0,data) {
  
  
  return " zero";
  }

function program6(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.unread_count) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.unread_count; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  return escapeExpression(stack1);
  }

function program8(depth0,data) {
  
  
  return "0";
  }

  stack1 = helpers.each.call(depth0, depth0.objects, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  });

this["PYO"]["templates"]["post_timeout_msg"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  


  return "<p class=\"timeout\">This message was not sent. You may have lost your connection to the internet. <a class=\"resend\" href=\"#\">Try again?</a> Or <a class=\"cancel\" href=\"#\">cancel this post</a>.</p>\n";
  });

this["PYO"]["templates"]["posts"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  var buffer = "", stack1, self=this, functionType="function", escapeExpression=this.escapeExpression;

function program1(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n<article class=\"post ";
  stack1 = helpers['if'].call(depth0, depth0.local, {hash:{},inverse:self.program(4, program4, data),fn:self.program(2, program2, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  stack1 = helpers['if'].call(depth0, depth0.unread, {hash:{},inverse:self.noop,fn:self.program(11, program11, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\" data-author-id=\"";
  if (stack1 = helpers.author_id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.author_id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-post-id=\"";
  if (stack1 = helpers.post_id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-author-sequence=\"";
  if (stack1 = helpers.author_sequence_id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.author_sequence_id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-xhr-count=\"";
  if (stack1 = helpers.xhr_count) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.xhr_count; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-mark-read-url=\"";
  if (stack1 = helpers.mark_read_url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.mark_read_url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">\n\n  <header class=\"post-meta\">\n    ";
  stack1 = helpers.unless.call(depth0, depth0.local, {hash:{},inverse:self.noop,fn:self.program(13, program13, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n    <h3 class=\"byline vcard\">\n      <b class=\"title\">";
  if (stack1 = helpers.role) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.role; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + ":</b>\n      <span class=\"fn\">";
  if (stack1 = helpers.author) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.author; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</span>\n    </h3>\n    <time class=\"pubdate\" datetime=\"";
  if (stack1 = helpers.timestamp) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.timestamp; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" title=\"";
  if (stack1 = helpers.date) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.date; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + " at ";
  if (stack1 = helpers.time) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.time; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">";
  if (stack1 = helpers.naturaldate) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.naturaldate; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + " at ";
  if (stack1 = helpers.time) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.time; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</time>\n  </header>\n\n  <p class=\"post-text\">\n    ";
  stack1 = helpers['if'].call(depth0, depth0.local, {hash:{},inverse:self.program(33, program33, data),fn:self.program(31, program31, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n  </p>\n\n</article>\n";
  return buffer;
  }
function program2(depth0,data) {
  
  
  return " local";
  }

function program4(depth0,data) {
  
  var buffer = "", stack1;
  stack1 = helpers['if'].call(depth0, depth0.sms, {hash:{},inverse:self.program(7, program7, data),fn:self.program(5, program5, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  stack1 = helpers.unless.call(depth0, depth0.unread, {hash:{},inverse:self.noop,fn:self.program(9, program9, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  return buffer;
  }
function program5(depth0,data) {
  
  
  return " sms";
  }

function program7(depth0,data) {
  
  
  return " no-sms";
  }

function program9(depth0,data) {
  
  
  return " old";
  }

function program11(depth0,data) {
  
  
  return " unread";
  }

function program13(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n    <div class=\"sms-info details\" title=\"";
  stack1 = helpers['if'].call(depth0, depth0.from_sms, {hash:{},inverse:self.program(16, program16, data),fn:self.program(14, program14, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\">\n\n      <div class=\"details-body\" id=\"sms-post-";
  if (stack1 = helpers.post_id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "-details\">\n        ";
  stack1 = helpers['if'].call(depth0, depth0.from_sms, {hash:{},inverse:self.noop,fn:self.program(21, program21, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n\n        ";
  stack1 = helpers['if'].call(depth0, depth0.to_sms, {hash:{},inverse:self.noop,fn:self.program(23, program23, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n\n        ";
  stack1 = helpers.unless.call(depth0, depth0.from_sms, {hash:{},inverse:self.noop,fn:self.program(26, program26, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n      </div>\n\n      <a href=\"#sms-post-";
  if (stack1 = helpers.post_id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "-details\" class=\"summary\">";
  stack1 = helpers.unless.call(depth0, depth0.sms, {hash:{},inverse:self.noop,fn:self.program(29, program29, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "text messages sent/received</a>\n\n    </div>\n    ";
  return buffer;
  }
function program14(depth0,data) {
  
  
  return "Received by text.";
  }

function program16(depth0,data) {
  
  var buffer = "", stack1;
  stack1 = helpers['if'].call(depth0, depth0.to_sms, {hash:{},inverse:self.program(19, program19, data),fn:self.program(17, program17, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += " sent.";
  return buffer;
  }
function program17(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "Text";
  if (stack1 = helpers.plural_sms) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.plural_sms; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1);
  return buffer;
  }

function program19(depth0,data) {
  
  
  return "No texts";
  }

function program21(depth0,data) {
  
  
  return "Received by text. ";
  }

function program23(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "Text";
  if (stack1 = helpers.plural_sms) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.plural_sms; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + " sent";
  stack1 = helpers['if'].call(depth0, depth0.sms_recipients, {hash:{},inverse:self.noop,fn:self.program(24, program24, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += ".";
  return buffer;
  }
function program24(depth0,data) {
  
  var buffer = "", stack1;
  buffer += " to ";
  if (stack1 = helpers.sms_recipients) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.sms_recipients; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1);
  return buffer;
  }

function program26(depth0,data) {
  
  var stack1;
  stack1 = helpers.unless.call(depth0, depth0.to_sms, {hash:{},inverse:self.noop,fn:self.program(27, program27, data),data:data});
  if(stack1 || stack1 === 0) { return stack1; }
  else { return ''; }
  }
function program27(depth0,data) {
  
  
  return "No text messages sent.";
  }

function program29(depth0,data) {
  
  
  return "no ";
  }

function program31(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.text) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.text; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  return escapeExpression(stack1);
  }

function program33(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.text) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.text; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  if(stack1 || stack1 === 0) { return stack1; }
  else { return ''; }
  }

  stack1 = helpers.each.call(depth0, depth0.posts, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  });

this["PYO"]["templates"]["student_list"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; partials = partials || Handlebars.partials; data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n<div class=\"additems\">\n  ";
  stack1 = helpers['if'].call(depth0, depth0.group_add_student_url, {hash:{},inverse:self.noop,fn:self.program(2, program2, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n</div>\n";
  return buffer;
  }
function program2(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "<a href=\"";
  if (stack1 = helpers.group_add_student_url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_add_student_url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" class=\"action-addbulk ajax-link additem-village\">Signup Parents</a>";
  return buffer;
  }

  buffer += "<div class=\"navtitle\">\n  <a href=\"#\" class=\"action-showgroups\" title=\"List groups\">List groups</a>\n  <h2 class=\"group-name\">";
  if (stack1 = helpers.group_name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</h2>\n  <a href=\"";
  if (stack1 = helpers.group_url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" class=\"group-feed ajax-link\" data-group-name=\"";
  if (stack1 = helpers.group_name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-id=\"";
  if (stack1 = helpers.group_id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-students-url=\"";
  if (stack1 = helpers.group_students_url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_students_url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-resource-url=\"";
  if (stack1 = helpers.group_resource_url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_resource_url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-edit-url=\"";
  if (stack1 = helpers.group_edit_url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_edit_url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-add-student-url=\"";
  if (stack1 = helpers.group_add_student_url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_add_student_url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-group-add-students-bulk-url=\"";
  if (stack1 = helpers.group_add_students_bulk_url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_add_students_bulk_url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-removed=\"";
  if (stack1 = helpers.removed) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.removed; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">\n    Send a message to ";
  if (stack1 = helpers.group_name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\n  </a>\n</div>\n\n<ul class=\"itemlist students-list\">\n  ";
  stack1 = self.invokePartial(partials.student_list_items, 'student_list_items', depth0, helpers, partials, data);
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n</ul>\n\n";
  stack1 = helpers['if'].call(depth0, depth0.staff, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  });

this["PYO"]["templates"]["student_list_items"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [2,'>= 1.0.0-rc.3'];
helpers = helpers || Handlebars.helpers; data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data,depth1) {
  
  var buffer = "", stack1;
  buffer += "\n<li class=\"listitem student\">\n  <a href=\"";
  if (stack1 = helpers.village_uri) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.village_uri; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1);
  stack1 = helpers.unless.call(depth0, depth1.all_students, {hash:{},inverse:self.noop,fn:self.programWithDepth(program2, data, depth1),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\" class=\"ajax-link listitem-select\" data-id=\"";
  if (stack1 = helpers.id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-name=\"";
  if (stack1 = helpers.name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">\n    <span class=\"listitem-name\">";
  if (stack1 = helpers.name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</span>\n    <span class=\"unread";
  stack1 = helpers.unless.call(depth0, depth0.unread_count, {hash:{},inverse:self.noop,fn:self.program(4, program4, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\">\n      ";
  stack1 = helpers['if'].call(depth0, depth0.unread_count, {hash:{},inverse:self.program(8, program8, data),fn:self.program(6, program6, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n    </span>\n  </a>\n</li>\n";
  return buffer;
  }
function program2(depth0,data,depth2) {
  
  var buffer = "", stack1;
  buffer += "?group="
    + escapeExpression(((stack1 = depth2.group_id),typeof stack1 === functionType ? stack1.apply(depth0) : stack1));
  return buffer;
  }

function program4(depth0,data) {
  
  
  return " zero";
  }

function program6(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.unread_count) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.unread_count; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  return escapeExpression(stack1);
  }

function program8(depth0,data) {
  
  
  return "0";
  }

  stack1 = helpers.each.call(depth0, depth0.objects, {hash:{},inverse:self.noop,fn:self.programWithDepth(program1, data, depth0),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  });