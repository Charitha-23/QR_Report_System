let rolesData = [];
let usersData = [];

// ---------------- LOAD ROLES ----------------
async function loadRoles() {
    let res = await fetch("/api/roles");
    rolesData = await res.json();

    let select = document.getElementById("roleSelect");
    select.innerHTML = "";

    rolesData.forEach(r => {
        let opt = document.createElement("option");
        opt.value = r.role;
        opt.textContent = r.role;
        select.appendChild(opt);
    });
}

// ---------------- LOAD USERS ----------------
async function loadUsers() {
    let res = await fetch("/api/users");
    usersData = await res.json();

    let select = document.getElementById("userSelect");
    select.innerHTML = "";

    usersData.forEach(u => {
        let opt = document.createElement("option");
        opt.value = u.username;
        opt.textContent = u.username;
        select.appendChild(opt);
    });

    if (usersData.length > 0) {
        select.value = usersData[0].username;
        loadUserDetails();
    }
}

// ---------------- LOAD USER DETAILS ----------------
function loadUserDetails() {
    let username = document.getElementById("userSelect").value;

    let user = usersData.find(u => u.username === username);
    if (!user) return;

    document.getElementById("roleSelect").value = user.role;

    setCheckboxValues("divisions", user.allowed_divisions || []);
    setCheckboxValues("types", user.allowed_types || []);

    updatePermissionToggles(user.role);
}

// ---------------- UPDATE PERMISSIONS ----------------
function updatePermissionToggles(role) {

    let roleObj = rolesData.find(r => r.role === role);

    if (!roleObj || !roleObj.permissions) {
        document.getElementById("view").checked = false;
        document.getElementById("edit").checked = false;
        document.getElementById("delete").checked = false;
        document.getElementById("download").checked = false;
        return;
    }

    let p = roleObj.permissions;

    document.getElementById("view").checked = !!p.view;
    document.getElementById("edit").checked = !!p.edit;
    document.getElementById("delete").checked = !!p.delete;
    document.getElementById("download").checked = !!p.download;

    document.getElementById("roleBadge").textContent = role;

    // ✅ ONLY CHANGE: checkboxes are always enabled
    let disable = false;

    document.querySelectorAll("#divisions input, #types input")
        .forEach(cb => cb.disabled = disable);
}

// ---------------- CREATE CHECKBOX LIST ----------------
function fillCheckboxList(id, values) {
    let container = document.getElementById(id);
    container.innerHTML = "";

    values.forEach((v, index) => {
        let checkboxId = `${id}_${index}`;

        let div = document.createElement("div");
        div.className = "form-check";

        div.innerHTML = `
            <input class="form-check-input" type="checkbox" id="${checkboxId}" value="${v.name}">
            <label class="form-check-label" for="${checkboxId}">
                ${v.name}
            </label>
        `;

        div.querySelector("input").addEventListener("change", () => {
            updateCount(id);
        });

        container.appendChild(div);
    });
}

// ---------------- SET VALUES ----------------
function setCheckboxValues(id, values) {
    let checkboxes = document.querySelectorAll(`#${id} input`);

    checkboxes.forEach(cb => {
        cb.checked = values.includes(cb.value);
    });

    updateCount(id);
}

// ---------------- GET VALUES ----------------
function getSelected(id) {
    let checked = document.querySelectorAll(`#${id} input:checked`);
    return Array.from(checked).map(cb => cb.value);
}

// ---------------- SELECT ALL ----------------
function selectAll(id) {
    document.querySelectorAll(`#${id} input`).forEach(cb => cb.checked = true);
    updateCount(id);
}

// ---------------- CLEAR ALL ----------------
function clearAll(id) {
    document.querySelectorAll(`#${id} input`).forEach(cb => cb.checked = false);
    updateCount(id);
}

// ---------------- SEARCH ----------------
function filterOptions(input, id) {
    let filter = input.value.toLowerCase();

    document.querySelectorAll(`#${id} label`).forEach(label => {
        label.parentElement.style.display =
            label.textContent.toLowerCase().includes(filter) ? "" : "none";
    });
}

// ---------------- COUNT ----------------
function updateCount(id) {
    let count = document.querySelectorAll(`#${id} input:checked`).length;
    let labelId = id === "divisions" ? "divCount" : "typeCount";

    document.getElementById(labelId).textContent = `${count} selected`;
}

// ---------------- LOAD DROPDOWNS ----------------
async function loadDropdowns() {
    let res = await fetch("/api/dropdowns");
    let data = await res.json();

    fillCheckboxList("divisions", data.division || []);
    fillCheckboxList("types", data.report_type || []);
}

// ---------------- SAVE ----------------
async function saveUserAccess() {

    let username = document.getElementById("userSelect").value;
    let role = document.getElementById("roleSelect").value;

    let data = {
        username: username,
        role: role,
        allowed_divisions: getSelected("divisions"),
        allowed_types: getSelected("types")
    };

    await fetch("/api/update-user-role", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    alert("Access updated");

    await loadUsers();
}

// ---------------- EVENTS ----------------
document.getElementById("userSelect").addEventListener("change", loadUserDetails);

document.getElementById("roleSelect").addEventListener("change", () => {
    let role = document.getElementById("roleSelect").value;
    updatePermissionToggles(role);
});

// ---------------- INIT ----------------
async function init() {
    await loadRoles();
    await loadDropdowns();
    await loadUsers();
}

init();