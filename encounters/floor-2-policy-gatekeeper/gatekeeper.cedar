// The Policy Gatekeeper's rulebook. Cedar is the name of the policy language.
// Every tool call is an action (Action::"file_editor", Action::"shell"). Anything no rule permits is denied.

// file_editor works on any path inside the floor folder, as long as the path does not climb out with ".."
permit(principal, action == Action::"file_editor", resource)
when {
    context.input has path &&
    (context.input.path like "*/floor-2-policy-gatekeeper/*" ||
     context.input.path like "*/floor-2-policy-gatekeeper") &&
    !(context.input.path like "*..*")
};

// shell runs only commands that name the floor folder
permit(principal, action == Action::"shell", resource)
when {
    context.input has command &&
    context.input.command like "*floor-2-policy-gatekeeper*"
};

// a forbid rule always wins over a permit: no command climbs out, reaches the home folder or deletes recursively
forbid(principal, action == Action::"shell", resource)
when {
    context.input has command &&
    (context.input.command like "*..*" ||
     context.input.command like "*~*" ||
     context.input.command like "*rm -rf*" ||
     context.input.command like "*sudo*")
};
