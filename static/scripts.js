function completeHabit(habitId) {
    fetch(`/complete/${habitId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove habit from active list
            const habitElem = document.getElementById(`habit-${habitId}`);
            if (habitElem) habitElem.remove();

            // Add habit to completed list
            const completedList = document.getElementById('completed-habits-list');
            const li = document.createElement('li');
            li.id = `completed-${habitId}`;
            li.className = 'list-group-item list-group-item-success d-flex justify-content-between align-items-center';
            li.innerHTML = `${data.habit_name} <span class="badge bg-success rounded-pill">Completed</span>`;
            completedList.appendChild(li);
        } else {
            alert('Error completing habit.');
        }
    })
    .catch(err => console.error('Error:', err));
}
