let schoolclass = ''

let replacementsTable = document.getElementById('replacementsTable')
let notificationsTable = document.getElementById('notificationsTable')
const days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Sammstag", "Sonntag"];
let settingsForm = $('#settings')
let reloadButton = document
  .getElementById('reload')
  .addEventListener('click', function (e) {
    e.preventDefault()
    load()
  })

function load() {
  fetch(`/v2.0/replacements//${schoolclass}`)
    .then(r => r.json())
    .then(displayReplacements);

  fetch('/v2.0/notifications//')
    .then(r => r.json())
    .then(displayNotifications);
}

function displayReplacements(r) {
  $(replacementsTable).find('tr').remove()
  let date = new Date(r.meta.date);
  console.log(date)
  let planDate = ''
  if (r.replacements.length === 0) {
    planDate += '<b>Keine</b> '
  }
  planDate += 'Vertretungen '
  planDate += `am ${days[date.getDay() - 1]}, `
  planDate += ('0' + date.getDate()).slice(-2) + '.'
  planDate += ('0' + (date.getMonth() + 1)).slice(-2) + '.'
  planDate += date.getFullYear()
  if (schoolclass !== '') {
    planDate += ' für die '
    planDate += schoolclass.replace('%', '')
  }
  $('.planDate').each(function () {
    $(this).html(planDate);
  })
  planWeek = ' — '
  if (r.week !== '') {
    planWeek += `<b>${r.week}</b> `
  }
  planWeek += 'Woche'
  if (r.week === '') {
    planWeek += ` ist unbekannt`
  }
  $('.planWeek').each(function () {
    $(this).html(planWeek);
  })
  $.each(r.replacements, function (i, val) {
    let row = replacementsTable.insertRow();

    let cell1 = row.insertCell(0);
    let cell2 = row.insertCell(1);
    let cell3 = row.insertCell(2);
    let cell4 = row.insertCell(3);
    let cell5 = row.insertCell(4);

    cell1.innerText = val.schoolclass;
    cell2.innerText = val.schoolhour;
    cell3.innerText = val.schoolsubject;
    if (!val.schoolsubject) {
      cell3.className = 'bi-arrow-right';
    }
    cell4.innerText = val.schoolroom;
    cell5.className = 'bi-check2-circle';
    if (val.dropped === true) {
      cell5.className = 'bi-x-circle-fill';
    }
  })
}

function displayNotifications(n) {
  $(notificationsTable).find('tr').remove()
  $.each(n.notifications, function (i, val) {
    let row = notificationsTable.insertRow()
    let cell1 = row.insertCell()
    cell1.innerText = val
  })
}

$( "#settings" ).submit(function( event ) {
  event.preventDefault();
  console.log('submit');
  schoolclass = $('#schoolclass').val();
  localStorage.schoolclass = schoolclass;
  load();
  return;
})

$(window).on('load', function () {
  M.AutoInit();
      if (!typeof(localStorage)) {
        alert("There are missing dependencies. This page might won't work properly!")
    } else {
        if (typeof localStorage.schoolclass !== 'undefined') {
            schoolclass = localStorage.schoolclass;
            $("#schoolclass").val(schoolclass);
        }
    }
  load()
})
