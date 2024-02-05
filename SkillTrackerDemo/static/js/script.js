// Function to hide the flash message
function hideFlashMessage() {
    const flashMessage = document.querySelector(".alert");
    if (flashMessage) {
      flashMessage.style.transition = "opacity 0.5s linear"; // this creates a fade-out effect
      flashMessage.style.opacity = "0"; // start the fade-out effect
  
      // Wait for the fade-out effect to finish before removing the element
      setTimeout(() => {
        flashMessage.remove();
      }, 500); // time in milliseconds (500ms for the fade-out effect)
    }
  }
  
  // Dismiss the flash message after 2 seconds
  window.addEventListener("load", () => {
    setTimeout(hideFlashMessage, 2000); // 2000 milliseconds = 2 seconds
  });
  
  // reports
  document.addEventListener("DOMContentLoaded", function () {
    var ctx = document.getElementById("progressReportChart").getContext("2d");
    var progressReportChart = new Chart(ctx, {
      type: "bar", // Change chart type as needed (bar, line, pie, etc.)
      data: {
        labels: ["Student 1", "Student 2", "Student 3"], // Example labels
        datasets: [
          {
            label: "Progress (%)",
            data: [75, 50, 90], // Example data
            backgroundColor: [
              "rgba(54, 162, 235, 0.2)",
              "rgba(255, 206, 86, 0.2)",
              "rgba(75, 192, 192, 0.2)",
            ],
            borderColor: [
              "rgba(54, 162, 235, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(75, 192, 192, 1)",
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  });
  
  // add competency
  document.addEventListener("DOMContentLoaded", () => {
    const addCompetencyForm = document.getElementById("addCompetencyForm");
  
    addCompetencyForm.addEventListener("submit", function (e) {
      e.preventDefault();
  
      const formData = new FormData(this);
      fetch("/add_competency", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            // If the competency was successfully added, reload the page to show the updated list
            window.location.reload();
          } else {
            // If there was a problem adding the competency, log the error message
            console.error(data.message);
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  });
  
  function confirmDelete(competencyId) {
    if (confirm("Are you sure you want to delete this competency?")) {
      fetch("/delete_competency/" + competencyId, {
        method: "POST",
        // No CSRF token header included
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      })
        .then((response) => {
          if (response.ok) {
            window.location.reload(); // Reload the page to reflect changes
          } else {
            alert("Error deleting competency.");
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  }
// learning outcome delete
function deleteLearningOutcome(outcomeId) {
    if (confirm("Are you sure you want to delete this learning outcome?")) {
      fetch(`/delete_learning_outcome/${outcomeId}`, { 
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          alert(data.message);
          window.location.reload();
        } else {
          throw new Error(data.message);
        }
      })
      .catch(error => console.error('Error deleting learning outcome:', error));
    }
  }
  
  
  
  function showAddLearningOutcomeModal(competencyId) {
    // Set competencyId in the hidden input field of the add learning outcome modal
    document.getElementById('addOutcomeCompetencyId').value = competencyId;
    // Show the modal
    var addLearningOutcomeModal = new bootstrap.Modal(document.getElementById('addLearningOutcomeModal'));
    addLearningOutcomeModal.show();
  }
  // adding learning outccome
  document.addEventListener("DOMContentLoaded", () => {
      const addLearningOutcomeForm = document.getElementById("addLearningOutcomeForm");
      addLearningOutcomeForm.addEventListener("submit", function(e) {
          e.preventDefault();
  
          const formData = new FormData(this);
          fetch("/add_learning_outcome", {
              method: "POST",
              body: formData,
          })
          .then(response => response.json())
          .then(data => {
              if (data.status === "success") {
                  alert(data.message); // Show success message
                  window.location.reload(); // Optionally reload the page or update the UI to show the new learning outcome
              } else {
                  alert(data.message); // Show error message
              }
          })
          .catch(error => {
              console.error("Error adding learning outcome:", error);
              alert("An error occurred while adding the learning outcome.");
          });
      });
  });
  
  // editing learning outcome
  function editLearningOutcome(outcomeId, competencyId) {
    fetch(`/get_learning_outcome_details/${outcomeId}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // Set the outcomeId as a data attribute on the form
        const form = document.getElementById('editLearningOutcomeForm');
        form.dataset.outcomeId = outcomeId;
  
        // Populate the form fields with the data fetched
        document.getElementById('editOutcomeDescription').value = data.description;
  
        // Show the modal for editing
        const editModal = new bootstrap.Modal(document.getElementById('editLearningOutcomeModal'));
        editModal.show();
      })
      .catch(error => console.error('Error fetching learning outcome details:', error));
  }
  
  
  document.addEventListener("DOMContentLoaded", () => {
      const editForm = document.getElementById('editLearningOutcomeForm');
      if (editForm) {
          editForm.addEventListener('submit', function(e) {
              e.preventDefault();
  
              const outcomeId = this.getAttribute('data-outcome-id'); // Ensure this attribute is set correctly
              const formData = new FormData(this);
  
              fetch(`/edit_learning_outcome/${outcomeId}`, {
                  method: 'POST',
                  body: formData,
              })
              .then(response => response.json()) // Expecting JSON response from Flask
              .then(data => {
                  if (data.status === 'success') {
                      alert('Learning outcome updated successfully!');
                      window.location.reload(); // Reload the page to reflect changes
                  } else {
                      alert(`Error updating learning outcome: ${data.message}`);
                  }
              })
              .catch(error => {
                  console.error('Error:', error);
              });
          });
      }
  });
  
  