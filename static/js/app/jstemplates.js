this["PYO"] = this["PYO"] || {};
this["PYO"]["templates"] = this["PYO"]["templates"] || {};

this["PYO"]["templates"]["ajax_error_msg"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
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

this["PYO"]["templates"]["autocomplete_input"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  
  return " new";
  }

function program3(depth0,data) {
  
  var buffer = "", stack1;
  if (stack1 = helpers.prefix) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.prefix; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "-";
  return buffer;
  }

function program5(depth0,data) {
  
  var stack1;
  stack1 = helpers['if'].call(depth0, depth0.responseDataVal, {hash:{},inverse:self.noop,fn:self.program(6, program6, data),data:data});
  if(stack1 || stack1 === 0) { return stack1; }
  else { return ''; }
  }
function program6(depth0,data) {
  
  var buffer = "", stack1;
  buffer += " data-";
  if (stack1 = helpers.responseDataName) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.responseDataName; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "=\"";
  if (stack1 = helpers.responseDataVal) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.responseDataVal; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\"";
  return buffer;
  }

function program8(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.labelText) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.labelText; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  return escapeExpression(stack1);
  }

function program10(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.inputText) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.inputText; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  return escapeExpression(stack1);
  }

function program12(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n    <span class=\"token-context\">";
  if (stack1 = helpers.inputContext) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.inputContext; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</span>\n    ";
  return buffer;
  }

  buffer += "<span class=\"token";
  stack1 = helpers['if'].call(depth0, depth0.newInput, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\">\n  <input class=\"token-toggle";
  stack1 = helpers['if'].call(depth0, depth0.newInput, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\" type=\"checkbox\" name=\"";
  if (stack1 = helpers.typeName) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.typeName; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" id=\"";
  stack1 = helpers['if'].call(depth0, depth0.prefix, {hash:{},inverse:self.noop,fn:self.program(3, program3, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  if (stack1 = helpers.typeName) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.typeName; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "-";
  if (stack1 = helpers.index) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.index; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" value=\"";
  if (stack1 = helpers.id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\"";
  stack1 = helpers['if'].call(depth0, depth0.responseDataName, {hash:{},inverse:self.noop,fn:self.program(5, program5, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += " checked />\n  <span class=\"token-body\">\n    <label class=\"token-status\" for=\"";
  stack1 = helpers['if'].call(depth0, depth0.prefix, {hash:{},inverse:self.noop,fn:self.program(3, program3, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  if (stack1 = helpers.typeName) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.typeName; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "-";
  if (stack1 = helpers.index) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.index; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">";
  stack1 = helpers['if'].call(depth0, depth0.labelText, {hash:{},inverse:self.program(10, program10, data),fn:self.program(8, program8, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "</label>\n    <span class=\"token-text\">";
  if (stack1 = helpers.inputText) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.inputText; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</span>\n    ";
  stack1 = helpers['if'].call(depth0, depth0.inputContext, {hash:{},inverse:self.noop,fn:self.program(12, program12, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n  </span>\n</span>\n";
  return buffer;
  });

this["PYO"]["templates"]["autocomplete_suggestion"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n<li>\n  <a href=\"#\" class=\"option";
  stack1 = helpers['if'].call(depth0, depth0.newSuggestion, {hash:{},inverse:self.noop,fn:self.program(2, program2, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\"";
  stack1 = helpers['if'].call(depth0, depth0.id, {hash:{},inverse:self.noop,fn:self.program(4, program4, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  stack1 = helpers['if'].call(depth0, depth0.type, {hash:{},inverse:self.noop,fn:self.program(6, program6, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += " data-text=\"";
  if (stack1 = helpers.text) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.text; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" data-context=\"";
  if (stack1 = helpers.context) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.context; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\"";
  stack1 = helpers['if'].call(depth0, depth0.responseDataName, {hash:{},inverse:self.noop,fn:self.program(8, program8, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += ">\n    <span class=\"suggestion-text\">";
  stack1 = helpers['if'].call(depth0, depth0.typedText, {hash:{},inverse:self.program(13, program13, data),fn:self.program(11, program11, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "</span>\n    <span class=\"suggestion-context\">";
  stack1 = helpers['if'].call(depth0, depth0.typedContext, {hash:{},inverse:self.program(17, program17, data),fn:self.program(15, program15, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "</span>\n  </a>\n</li>\n";
  return buffer;
  }
function program2(depth0,data) {
  
  
  return " new";
  }

function program4(depth0,data) {
  
  var buffer = "", stack1;
  buffer += " data-id=\"";
  if (stack1 = helpers.id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\"";
  return buffer;
  }

function program6(depth0,data) {
  
  var buffer = "", stack1;
  buffer += " data-type=\"";
  if (stack1 = helpers.type) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.type; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\"";
  return buffer;
  }

function program8(depth0,data) {
  
  var stack1;
  stack1 = helpers['if'].call(depth0, depth0.responseDataVal, {hash:{},inverse:self.noop,fn:self.program(9, program9, data),data:data});
  if(stack1 || stack1 === 0) { return stack1; }
  else { return ''; }
  }
function program9(depth0,data) {
  
  var buffer = "", stack1;
  buffer += " data-";
  if (stack1 = helpers.responseDataName) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.responseDataName; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "=\"";
  if (stack1 = helpers.responseDataVal) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.responseDataVal; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\"";
  return buffer;
  }

function program11(depth0,data) {
  
  var buffer = "", stack1;
  if (stack1 = helpers.preText) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.preText; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "<b>";
  if (stack1 = helpers.typedText) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.typedText; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</b>";
  if (stack1 = helpers.postText) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.postText; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1);
  return buffer;
  }

function program13(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.text) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.text; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  return escapeExpression(stack1);
  }

function program15(depth0,data) {
  
  var buffer = "", stack1;
  if (stack1 = helpers.preContext) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.preContext; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "<b>";
  if (stack1 = helpers.typedContext) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.typedContext; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</b>";
  if (stack1 = helpers.postContext) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.postContext; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1);
  return buffer;
  }

function program17(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.context) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.context; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  return escapeExpression(stack1);
  }

  stack1 = helpers.each.call(depth0, depth0.suggestions, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  });

this["PYO"]["templates"]["group_list"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); partials = this.merge(partials, Handlebars.partials); data = data || {};
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
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
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

this["PYO"]["templates"]["note_attachment_input"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression;


  buffer += "<input type=\"file\" id=\"attach-file-";
  if (stack1 = helpers.index) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.index; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" class=\"attach-value ie-fix-active\" name=\"attachment\" />\n";
  return buffer;
  });

this["PYO"]["templates"]["post_timeout_msg"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  var buffer = "", stack1, self=this;

function program1(depth0,data) {
  
  
  return "Please try again. (<a class=\"cancel\" href=\"#\">remove this post</a>)";
  }

function program3(depth0,data) {
  
  
  return "<a class=\"resend\" href=\"#\">Try again?</a> Or <a class=\"cancel\" href=\"#\">cancel this post</a>.";
  }

  buffer += "<p class=\"timeout\">This message was not sent. You may have lost your connection to the internet. ";
  stack1 = helpers['if'].call(depth0, depth0.attachments, {hash:{},inverse:self.program(3, program3, data),fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "</p>\n";
  return buffer;
  });

this["PYO"]["templates"]["posts"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  var buffer = "", stack1, self=this, functionType="function", escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing;

function program1(depth0,data) {
  
  var buffer = "", stack1, stack2;
  buffer += "\n<article class=\"post post-type-"
    + escapeExpression(((stack1 = ((stack1 = depth0.type),stack1 == null || stack1 === false ? stack1 : stack1.name)),typeof stack1 === functionType ? stack1.apply(depth0) : stack1));
  stack2 = helpers['if'].call(depth0, depth0.pending, {hash:{},inverse:self.program(4, program4, data),fn:self.program(2, program2, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  stack2 = helpers['if'].call(depth0, depth0.mine, {hash:{},inverse:self.program(16, program16, data),fn:self.program(14, program14, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  stack2 = helpers['if'].call(depth0, depth0.attachments, {hash:{},inverse:self.noop,fn:self.program(19, program19, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "\" data-author-id=\"";
  if (stack2 = helpers.author_id) { stack2 = stack2.call(depth0, {hash:{},data:data}); }
  else { stack2 = depth0.author_id; stack2 = typeof stack2 === functionType ? stack2.apply(depth0) : stack2; }
  buffer += escapeExpression(stack2)
    + "\" data-post-id=\"";
  if (stack2 = helpers.post_id) { stack2 = stack2.call(depth0, {hash:{},data:data}); }
  else { stack2 = depth0.post_id; stack2 = typeof stack2 === functionType ? stack2.apply(depth0) : stack2; }
  buffer += escapeExpression(stack2)
    + "\" data-author-sequence=\"";
  if (stack2 = helpers.author_sequence_id) { stack2 = stack2.call(depth0, {hash:{},data:data}); }
  else { stack2 = depth0.author_sequence_id; stack2 = typeof stack2 === functionType ? stack2.apply(depth0) : stack2; }
  buffer += escapeExpression(stack2)
    + "\" data-xhr-count=\"";
  if (stack2 = helpers.xhr_count) { stack2 = stack2.call(depth0, {hash:{},data:data}); }
  else { stack2 = depth0.xhr_count; stack2 = typeof stack2 === functionType ? stack2.apply(depth0) : stack2; }
  buffer += escapeExpression(stack2)
    + "\" data-mark-read-url=\"";
  if (stack2 = helpers.mark_read_url) { stack2 = stack2.call(depth0, {hash:{},data:data}); }
  else { stack2 = depth0.mark_read_url; stack2 = typeof stack2 === functionType ? stack2.apply(depth0) : stack2; }
  buffer += escapeExpression(stack2)
    + "\">\n\n  <header class=\"post-header\">\n    <time class=\"pubdate\"";
  stack2 = helpers['if'].call(depth0, depth0.timestamp, {hash:{},inverse:self.noop,fn:self.program(21, program21, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += " title=\"";
  if (stack2 = helpers.timestamp_display) { stack2 = stack2.call(depth0, {hash:{},data:data}); }
  else { stack2 = depth0.timestamp_display; stack2 = typeof stack2 === functionType ? stack2.apply(depth0) : stack2; }
  buffer += escapeExpression(stack2)
    + "\">\n      ";
  if (stack2 = helpers.timestamp_display) { stack2 = stack2.call(depth0, {hash:{},data:data}); }
  else { stack2 = depth0.timestamp_display; stack2 = typeof stack2 === functionType ? stack2.apply(depth0) : stack2; }
  buffer += escapeExpression(stack2)
    + "\n    </time>\n\n    <h3 class=\"byline vcard\">\n      <span class=\"fn\">";
  stack2 = helpers['if'].call(depth0, depth0.school_staff, {hash:{},inverse:self.program(25, program25, data),fn:self.program(23, program23, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "</span>\n    </h3>\n\n    ";
  stack2 = helpers.unless.call(depth0, ((stack1 = depth0.type),stack1 == null || stack1 === false ? stack1 : stack1.is_note), {hash:{},inverse:self.noop,fn:self.program(27, program27, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "\n  </header>\n\n  <div class=\"post-body\">\n    ";
  stack2 = helpers['if'].call(depth0, depth0.attachments, {hash:{},inverse:self.noop,fn:self.program(46, program46, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "\n    <div class=\"post-text\">\n      <p>";
  stack2 = helpers['if'].call(depth0, depth0.pending, {hash:{},inverse:self.program(54, program54, data),fn:self.program(52, program52, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "</p>\n    </div>\n  </div>\n\n</article>\n";
  return buffer;
  }
function program2(depth0,data) {
  
  
  return " pending";
  }

function program4(depth0,data) {
  
  var buffer = "", stack1;
  stack1 = helpers['if'].call(depth0, depth0.from_sms, {hash:{},inverse:self.program(7, program7, data),fn:self.program(5, program5, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  stack1 = helpers.unless.call(depth0, depth0.unread, {hash:{},inverse:self.noop,fn:self.program(12, program12, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  return buffer;
  }
function program5(depth0,data) {
  
  
  return " from-sms";
  }

function program7(depth0,data) {
  
  var stack1;
  stack1 = helpers['if'].call(depth0, depth0.to_sms, {hash:{},inverse:self.program(10, program10, data),fn:self.program(8, program8, data),data:data});
  if(stack1 || stack1 === 0) { return stack1; }
  else { return ''; }
  }
function program8(depth0,data) {
  
  
  return " sms";
  }

function program10(depth0,data) {
  
  
  return " no-sms";
  }

function program12(depth0,data) {
  
  
  return " old";
  }

function program14(depth0,data) {
  
  
  return " mine";
  }

function program16(depth0,data) {
  
  var stack1;
  stack1 = helpers['if'].call(depth0, depth0.unread, {hash:{},inverse:self.noop,fn:self.program(17, program17, data),data:data});
  if(stack1 || stack1 === 0) { return stack1; }
  else { return ''; }
  }
function program17(depth0,data) {
  
  
  return " unread";
  }

function program19(depth0,data) {
  
  
  return " has-attachment";
  }

function program21(depth0,data) {
  
  var buffer = "", stack1;
  buffer += " datetime=\"";
  if (stack1 = helpers.timestamp) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.timestamp; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\"";
  return buffer;
  }

function program23(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.author) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.author; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  return escapeExpression(stack1);
  }

function program25(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.role) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.role; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  return escapeExpression(stack1);
  }

function program27(depth0,data) {
  
  var buffer = "", stack1, stack2;
  buffer += "\n      <div class=\"post-meta\">\n        ";
  stack2 = helpers['if'].call(depth0, ((stack1 = depth0.type),stack1 == null || stack1 === false ? stack1 : stack1.is_message), {hash:{},inverse:self.program(43, program43, data),fn:self.program(28, program28, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += "\n      </div>\n    ";
  return buffer;
  }
function program28(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n          ";
  stack1 = helpers['if'].call(depth0, depth0.sms, {hash:{},inverse:self.program(41, program41, data),fn:self.program(29, program29, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n        ";
  return buffer;
  }
function program29(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n            <input type=\"checkbox\" id=\"recipients-toggle-";
  if (stack1 = helpers.post_id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">\n            <label for=\"recipients-toggle-";
  if (stack1 = helpers.post_id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" title=\"more information\">show/hide</label>\n            <p class=\"recipients\">\n            ";
  stack1 = helpers['if'].call(depth0, depth0.pending, {hash:{},inverse:self.program(36, program36, data),fn:self.program(30, program30, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n            </p>\n          ";
  return buffer;
  }
function program30(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n              ";
  stack1 = helpers['if'].call(depth0, depth0.to_sms, {hash:{},inverse:self.noop,fn:self.program(31, program31, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n            ";
  return buffer;
  }
function program31(depth0,data) {
  
  var buffer = "", stack1, stack2, options;
  buffer += "Sending text";
  options = {hash:{},inverse:self.noop,fn:self.program(32, program32, data),data:data};
  stack2 = ((stack1 = helpers.plural || depth0.plural),stack1 ? stack1.call(depth0, depth0.sms_recipients, options) : helperMissing.call(depth0, "plural", depth0.sms_recipients, options));
  if(stack2 || stack2 === 0) { buffer += stack2; }
  stack2 = helpers['if'].call(depth0, depth0.sms_recipients, {hash:{},inverse:self.noop,fn:self.program(34, program34, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += ".";
  return buffer;
  }
function program32(depth0,data) {
  
  
  return "s";
  }

function program34(depth0,data) {
  
  var buffer = "", stack1, options;
  buffer += " to ";
  options = {hash:{},data:data};
  buffer += escapeExpression(((stack1 = helpers.join || depth0.join),stack1 ? stack1.call(depth0, depth0.sms_recipients, ", ", options) : helperMissing.call(depth0, "join", depth0.sms_recipients, ", ", options)));
  return buffer;
  }

function program36(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n              ";
  stack1 = helpers['if'].call(depth0, depth0.from_sms, {hash:{},inverse:self.noop,fn:self.program(37, program37, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n              ";
  stack1 = helpers['if'].call(depth0, depth0.to_sms, {hash:{},inverse:self.noop,fn:self.program(39, program39, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n            ";
  return buffer;
  }
function program37(depth0,data) {
  
  
  return "Sent from phone. ";
  }

function program39(depth0,data) {
  
  var buffer = "", stack1, stack2, options;
  buffer += "Text";
  options = {hash:{},inverse:self.noop,fn:self.program(32, program32, data),data:data};
  stack2 = ((stack1 = helpers.plural || depth0.plural),stack1 ? stack1.call(depth0, depth0.sms_recipients, options) : helperMissing.call(depth0, "plural", depth0.sms_recipients, options));
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += " sent";
  stack2 = helpers['if'].call(depth0, depth0.sms_recipients, {hash:{},inverse:self.noop,fn:self.program(34, program34, data),data:data});
  if(stack2 || stack2 === 0) { buffer += stack2; }
  buffer += ".";
  return buffer;
  }

function program41(depth0,data) {
  
  
  return "\n            No text messages sent.\n          ";
  }

function program43(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n          ";
  stack1 = helpers['if'].call(depth0, depth0.present, {hash:{},inverse:self.noop,fn:self.program(44, program44, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n        ";
  return buffer;
  }
function program44(depth0,data) {
  
  var buffer = "", stack1, options;
  buffer += "\n            <input type=\"checkbox\" id=\"recipients-toggle-";
  if (stack1 = helpers.post_id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">\n            <label for=\"recipients-toggle-";
  if (stack1 = helpers.post_id) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.post_id; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" title=\"more information\">show/hide</label>\n            <p class=\"recipients\">With ";
  options = {hash:{},data:data};
  buffer += escapeExpression(((stack1 = helpers.join || depth0.join),stack1 ? stack1.call(depth0, depth0.present, ", ", options) : helperMissing.call(depth0, "join", depth0.present, ", ", options)))
    + ".</p>\n          ";
  return buffer;
  }

function program46(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "\n    <div class=\"attachments\">\n      <ul>\n        ";
  stack1 = helpers.each.call(depth0, depth0.attachments, {hash:{},inverse:self.noop,fn:self.programWithDepth(47, program47, data, depth0),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n      </ul>\n    </div>\n    ";
  return buffer;
  }
function program47(depth0,data,depth1) {
  
  var buffer = "", stack1;
  buffer += "\n        <li>";
  stack1 = helpers['if'].call(depth0, depth1.pending, {hash:{},inverse:self.program(50, program50, data),fn:self.program(48, program48, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "</li>\n        ";
  return buffer;
  }
function program48(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  return escapeExpression(stack1);
  }

function program50(depth0,data) {
  
  var buffer = "", stack1;
  buffer += "<a href=\"";
  if (stack1 = helpers.url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\">";
  if (stack1 = helpers.name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "</a>";
  return buffer;
  }

function program52(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.text) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.text; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  return escapeExpression(stack1);
  }

function program54(depth0,data) {
  
  var stack1;
  if (stack1 = helpers.text) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.text; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  if(stack1 || stack1 === 0) { return stack1; }
  else { return ''; }
  }

  stack1 = helpers.each.call(depth0, depth0.objects, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  });

this["PYO"]["templates"]["student_list"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); partials = this.merge(partials, Handlebars.partials); data = data || {};
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

  buffer += "<div class=\"navtitle\">\n  <a href=\"#\" class=\"action-showgroups\">\n    <span data-icon=\"users-list\"> </span>\n    <span class=\"tooltip\">Show all groups</span>\n  </a>\n  <h2 class=\"group-name\">\n    <a href=\"";
  if (stack1 = helpers.group_url) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_url; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\" class=\"ajax-link group-dashboard\" data-group-name=\"";
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
    + "\">\n      ";
  if (stack1 = helpers.group_name) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.group_name; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1)
    + "\n    </a>\n  </h2>\n</div>\n\n<ul class=\"itemlist students-list\">\n  ";
  stack1 = self.invokePartial(partials.student_list_items, 'student_list_items', depth0, helpers, partials, data);
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n</ul>\n\n";
  stack1 = helpers['if'].call(depth0, depth0.staff, {hash:{},inverse:self.noop,fn:self.program(1, program1, data),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  });

this["PYO"]["templates"]["student_list_items"] = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  var buffer = "", stack1, functionType="function", escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data,depth1) {
  
  var buffer = "", stack1;
  buffer += "\n<li class=\"listitem student\">\n  <a href=\"";
  if (stack1 = helpers.village_uri) { stack1 = stack1.call(depth0, {hash:{},data:data}); }
  else { stack1 = depth0.village_uri; stack1 = typeof stack1 === functionType ? stack1.apply(depth0) : stack1; }
  buffer += escapeExpression(stack1);
  stack1 = helpers.unless.call(depth0, depth1.all_students, {hash:{},inverse:self.noop,fn:self.programWithDepth(2, program2, data, depth1),data:data});
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

  stack1 = helpers.each.call(depth0, depth0.objects, {hash:{},inverse:self.noop,fn:self.programWithDepth(1, program1, data, depth0),data:data});
  if(stack1 || stack1 === 0) { buffer += stack1; }
  buffer += "\n";
  return buffer;
  });