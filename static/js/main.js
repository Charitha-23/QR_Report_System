/* ======================================================
Upload Report
====================================================== */

const form = document.getElementById("uploadForm")

if (form) {

form.addEventListener("submit", async function(e){

e.preventDefault()

const message = document.getElementById("message")

message.innerHTML = `
<div class="alert alert-info">
Uploading report...
</div>
`

const formData = new FormData(form)

try{

const response = await fetch("/upload-report",{
method:"POST",
body:formData
})

const result = await response.json()

if(response.ok){

message.innerHTML = `
<div class="alert alert-success">
✅ File uploaded successfully!
</div>
`

form.reset()

setTimeout(()=>{
message.innerHTML = ""
},3000)

}else{

message.innerHTML = `
<div class="alert alert-danger">
${result.error || "Upload failed"}
</div>
`

}

}catch(error){

message.innerHTML = `
<div class="alert alert-danger">
Server error during upload
</div>
`

}

})

}


/* ======================================================
Search Reports
====================================================== */

async function searchReports(){

const queryInput = document.getElementById("searchInput")

if(!queryInput) return

const query = queryInput.value.trim()

const resultsDiv = document.getElementById("results")

if(!query){

resultsDiv.innerHTML = `
<div class="alert alert-warning">
Please enter a search keyword
</div>
`
return

}

resultsDiv.innerHTML = `
<div class="text-center">
<div class="spinner-border text-primary"></div>
<p class="mt-2">Searching reports...</p>
</div>
`

try{

const response = await fetch(`/search?q=${query}`)
const data = await response.json()

resultsDiv.innerHTML = ""

if(data.length === 0){

resultsDiv.innerHTML = `
<div class="alert alert-secondary">
No reports found
</div>
`
return

}

data.forEach(report => {

const card = document.createElement("div")

card.className = "card shadow-sm mb-3"

card.innerHTML = `

<div class="card-body">

<h5 class="card-title">
${report.report_name}
</h5>

<p class="card-text text-muted">
${report.ai_summary || "No AI summary available"}
</p>

<a href="/${report.file_path}" 
target="_blank" 
class="btn btn-primary btn-sm">
Open Report
</a>

</div>
`

resultsDiv.appendChild(card)

})

}catch(err){

resultsDiv.innerHTML = `
<div class="alert alert-danger">
Search failed
</div>
`

}

}


/* ======================================================
ENTER KEY SEARCH
====================================================== */

const searchInput = document.getElementById("searchInput")

if(searchInput){

searchInput.addEventListener("keypress", function(e){

if(e.key === "Enter"){

e.preventDefault()
searchReports()

}

})

}


/* ======================================================
Dashboard Stats
====================================================== */

async function loadStats(){

const totalReports = document.getElementById("totalReports")
const aiReports = document.getElementById("aiReports")

if(!totalReports || !aiReports) return

try{

const response = await fetch("/stats")
const data = await response.json()

totalReports.innerText = data.total_reports || 0
aiReports.innerText = data.ai_reports || 0

}catch(e){

console.log("Failed to load stats")

}

}

loadStats()


/* ======================================================
Dashboard Table (Report Management)
====================================================== */

async function loadDashboard(){

const table = document.getElementById("reportTable")

if(!table) return

table.innerHTML = `
<tr>
<td colspan="6" class="text-center">
<div class="spinner-border text-primary"></div>
<p class="mt-2">Loading reports...</p>
</td>
</tr>
`

try{

const response = await fetch("/all-reports")
const data = await response.json()

table.innerHTML = ""

if(data.length === 0){

table.innerHTML = `
<tr>
<td colspan="6" class="text-center">
No reports available
</td>
</tr>
`
return

}

data.forEach(report => {

const row = document.createElement("tr")

row.innerHTML = `

<td>${report.document_id}</td>

<td>${report.report_name}</td>

<td>${report.report_type}</td>

<td>${report.report_date}</td>


<td title="${report.ai_summary || 'No summary available'}">
${report.ai_summary ? report.ai_summary.substring(0,80)+"..." : "No summary"}
</td>


<td>

<button class="btn btn-sm btn-info"
onclick="viewReport('${report.report_name}', \`${report.ai_summary}\`, '${report.file_path}')">
View
</button>

<button class="btn btn-sm btn-danger"
onclick="deleteReport('${report.document_id}')">
Delete
</button>

</td>

`

table.appendChild(row)

})

}catch(error){

table.innerHTML = `
<tr>
<td colspan="6" class="text-danger text-center">
Failed to load reports
</td>
</tr>
`

}

}

loadDashboard()


/* ======================================================
Delete Report
====================================================== */

async function deleteReport(id){

if(!confirm("Are you sure you want to delete this report?")) return

try{

const response = await fetch(`/delete-report/${id}`,{
method:"DELETE"
})

if(response.ok){

alert("✅ Report deleted successfully")

loadDashboard()

}else{

alert("Delete failed")

}

}catch(e){

alert("Server error while deleting report")

}

}


/* ======================================================
View Report Modal
====================================================== */

function viewReport(name, summary, filePath){

document.getElementById("modalTitle").innerText = name

document.getElementById("modalSummary").innerText =
summary || "No AI summary available"

document.getElementById("openFileBtn").href = "/" + filePath.replaceAll("\\","/")

const modal = new bootstrap.Modal(
document.getElementById("reportModal")
)

modal.show()

}