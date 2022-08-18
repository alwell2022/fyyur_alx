window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

document.querySelectorAll(".delete").forEach(venue => {
    venue.addEventListener("click", (e) => {
    const venueID = e.target.dataset.id;
      e.target.parentElement.style.display = 'none';
      fetch(`/venues/${venueID}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(() => {

      })
      .catch(() => {
      	console.log("Could not delete the venue");
      });
    })
  });