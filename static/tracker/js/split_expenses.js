document.addEventListener('DOMContentLoaded', function() {
    const root = document.getElementById('split-root');
    const amount = parseFloat(root.dataset.amount);
    const userName = root.dataset.username;
    const userId = parseInt(root.dataset.userid);
    const friendName = root.dataset.friendname;
    const friendId = parseInt(root.dataset.friendid);

    const splitBtns = document.querySelectorAll('.split-btn');
    const splitHeading = document.getElementById('split-heading');
    const splitContent = document.getElementById('split-content');
    const moreOptionsBtn = document.getElementById('more-options-btn');
    const moreOptionsDiv = document.getElementById('more-options');
    const splitExpenseForm = document.getElementById('split-expense-form');
    const simpleOptionsDiv = document.getElementById('simple-options'); // Added

    // Default state
    let selectedMethod = 'equal';

    // Utility functions for rendering split methods (no changes here)
    function renderEqual() {
        splitHeading.textContent = 'Split equally';
        splitContent.innerHTML = `
            <table class="table">
                <tr>
                    <td>${userName}</td>
                    <td>Rs ${(amount/2).toFixed(2)}</td>
                </tr>
                <tr>
                    <td>${friendName}</td>
                    <td>Rs ${(amount/2).toFixed(2)}</td>
                </tr>
            </table>
            <div>Rs ${(amount/2).toFixed(2)}/person (2 people)</div>
        `;
        document.getElementById('user_share_field').value = (amount/2).toFixed(2);
        document.getElementById('friend_share_field').value = (amount/2).toFixed(2);
        document.getElementById('split_method_field').value = 'equal';
        document.getElementById('paid_by_field').value = userId;
    }

    function renderExact() {
        splitHeading.textContent = 'Split by exact amounts';
        splitContent.innerHTML = `
            <div>
                <label>${userName}: <input type="number" step="0.01" min="0" id="exact-user" class="form-control" style="width:100px;display:inline;"></label>
            </div>
            <div>
                <label>${friendName}: <input type="number" step="0.01" min="0" id="exact-friend" class="form-control" style="width:100px;display:inline;"></label>
            </div>
            <div id="exact-summary" class="mt-2"></div>
        `;
        function updateSummary() {
            const userVal = parseFloat(document.getElementById('exact-user').value) || 0;
            const friendVal = parseFloat(document.getElementById('exact-friend').value) || 0;
            const total = userVal + friendVal;
            let summary = `Rs ${total.toFixed(2)} of Rs ${amount.toFixed(2)}<br>`;
            summary += `Rs ${(amount-total).toFixed(2)} left`;
            document.getElementById('exact-summary').innerHTML = summary;
            document.getElementById('user_share_field').value = userVal.toFixed(2);
            document.getElementById('friend_share_field').value = friendVal.toFixed(2);
            document.getElementById('split_method_field').value = 'exact';
        }
        document.getElementById('exact-user').addEventListener('input', updateSummary);
        document.getElementById('exact-friend').addEventListener('input', updateSummary);
    }

    function renderPercent() {
        splitHeading.textContent = 'Split by percentage';
        splitContent.innerHTML = `
            <div>
                <label>${userName}: <input type="number" step="1" min="0" max="100" id="percent-user" class="form-control" style="width:80px;display:inline;"> %</label>
            </div>
            <div>
                <label>${friendName}: <input type="number" step="1" min="0" max="100" id="percent-friend" class="form-control" style="width:80px;display:inline;"> %</label>
            </div>
            <div id="percent-summary" class="mt-2"></div>
        `;
        function updateSummary() {
            const userVal = parseFloat(document.getElementById('percent-user').value) || 0;
            const friendVal = parseFloat(document.getElementById('percent-friend').value) || 0;
            const userAmt = amount * (userVal/100);
            const friendAmt = amount * (friendVal/100);
            let summary = `${userVal+friendVal}% of 100%<br>`;
            summary += `${(100-userVal-friendVal)}% left`;
            document.getElementById('percent-summary').innerHTML = summary;
            document.getElementById('user_share_field').value = userAmt.toFixed(2);
            document.getElementById('friend_share_field').value = friendAmt.toFixed(2);
            document.getElementById('split_method_field').value = 'percent';
        }
        document.getElementById('percent-user').addEventListener('input', updateSummary);
        document.getElementById('percent-friend').addEventListener('input', updateSummary);
    }

    function renderAdjust() {  
        splitHeading.textContent = 'Split by adjustments';
        splitContent.innerHTML = `
            <div>
                <label>${userName}: <span>Rs ${(amount/2).toFixed(2)}</span> + <input type="number" step="0.01" id="adjust-user" class="form-control" style="width:80px;display:inline;"></label>
            </div>
            <div>
                <label>${friendName}: <span>Rs ${(amount/2).toFixed(2)}</span> + <input type="number" step="0.01" id="adjust-friend" class="form-control" style="width:80px;display:inline;"></label>
            </div>
            <div id="adjust-summary" class="mt-2"></div>
        `;
        function updateSummary() {
            const userAdj = parseFloat(document.getElementById('adjust-user').value) || 0;
            const friendAdj = parseFloat(document.getElementById('adjust-friend').value) || 0;
            const userTotal = (amount/2) + userAdj;
            const friendTotal = (amount/2) + friendAdj;
            let summary = `${userName}: Rs ${userTotal.toFixed(2)}<br>${friendName}: Rs ${friendTotal.toFixed(2)}`;
            document.getElementById('adjust-summary').innerHTML = summary;
            document.getElementById('user_share_field').value = userTotal.toFixed(2);
            document.getElementById('friend_share_field').value = friendTotal.toFixed(2);
            document.getElementById('split_method_field').value = 'adjust';
        }
        document.getElementById('adjust-user').addEventListener('input', updateSummary);
        document.getElementById('adjust-friend').addEventListener('input', updateSummary);
    }

    function renderShares() {
        splitHeading.textContent = 'Split by shares';
        splitContent.innerHTML = `
            <div>
                <label>${userName}: <span>Rs ${(amount/2).toFixed(2)}</span> <input type="number" step="0.01" min="0.01" id="shares-user" class="form-control" style="width:80px;display:inline;" value="1"></label>
            </div>
            <div>
                <label>${friendName}: <span>Rs ${(amount/2).toFixed(2)}</span> <input type="number" step="0.01" min="0.01" id="shares-friend" class="form-control" style="width:80px;display:inline;" value="1"></label>
            </div>
            <div id="shares-summary" class="mt-2"></div>
        `;
        function updateSummary() {
            const userShares = parseFloat(document.getElementById('shares-user').value) || 1;
            const friendShares = parseFloat(document.getElementById('shares-friend').value) || 1;
            const totalShares = userShares + friendShares;
            const userAmt = amount * (userShares / totalShares);
            const friendAmt = amount * (friendShares / totalShares);
            let summary = `${userName}: Rs ${userAmt.toFixed(2)}<br>${friendName}: Rs ${friendAmt.toFixed(2)}`;
            document.getElementById('shares-summary').innerHTML = summary;
            document.getElementById('user_share_field').value = userAmt.toFixed(2);
            document.getElementById('friend_share_field').value = friendAmt.toFixed(2);
            document.getElementById('split_method_field').value = 'shares';
        }
        document.getElementById('shares-user').addEventListener('input', updateSummary);
        document.getElementById('shares-friend').addEventListener('input', updateSummary);
        updateSummary();
    }

    // Split method selection
    splitBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            splitBtns.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            selectedMethod = btn.dataset.method;
            if (selectedMethod === 'equal') renderEqual();
            else if (selectedMethod === 'exact') renderExact();
            else if (selectedMethod === 'percent') renderPercent();
            else if (selectedMethod === 'adjust') renderAdjust();
            else if (selectedMethod === 'shares') renderShares();
        });
    });

    // Initial render
    renderEqual();

    // **MODIFIED** Show/hide more options
    moreOptionsBtn.addEventListener('click', function() {
        const isHidden = moreOptionsDiv.style.display === 'none';
        if (isHidden) {
            // Show advanced options and hide simple ones
            moreOptionsDiv.style.display = 'block';
            simpleOptionsDiv.style.display = 'none';
            moreOptionsBtn.textContent = 'Fewer options';
            // Trigger the default advanced view
            renderEqual(); 
        } else {
            // Hide advanced options and show simple ones
            moreOptionsDiv.style.display = 'none';
            simpleOptionsDiv.style.display = 'block';
            moreOptionsBtn.textContent = 'More options';
            // Reset to the default simple radio button state
            document.getElementById('split_equal').checked = true;
            document.getElementById('split_equal').dispatchEvent(new Event('change'));
        }
    });

    // Handle radio buttons for simple split options
    document.querySelectorAll('input[name="split_type"]').forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'equal') {
                renderEqual();
                document.getElementById('paid_by_field').value = userId;
            } else if (this.value === 'user_full') {
                splitHeading.textContent = 'User is owed the full amount';
                splitContent.innerHTML = `<div>${friendName} owes you Rs ${amount.toFixed(2)}</div>`;
                document.getElementById('user_share_field').value = amount.toFixed(2);
                document.getElementById('friend_share_field').value = 0;
                document.getElementById('split_method_field').value = 'user_full';
                document.getElementById('paid_by_field').value = userId;
            } else if (this.value === 'friend_equal') {
                splitHeading.textContent = 'Friend paid, split equally';
                splitContent.innerHTML = `<div>You owe ${friendName} Rs ${(amount/2).toFixed(2)}</div>`;
                document.getElementById('user_share_field').value = (amount/2).toFixed(2);
                document.getElementById('friend_share_field').value = (amount/2).toFixed(2);
                document.getElementById('split_method_field').value = 'friend_equal';
                document.getElementById('paid_by_field').value = friendId;
            } else if (this.value === 'friend_full') {
                splitHeading.textContent = 'Friend is owed the full amount';
                splitContent.innerHTML = `<div>You owe ${friendName} Rs ${amount.toFixed(2)}</div>`;
                document.getElementById('user_share_field').value = 0;
                document.getElementById('friend_share_field').value = amount.toFixed(2);
                document.getElementById('split_method_field').value = 'friend_full';
                document.getElementById('paid_by_field').value = friendId;
            }
        });
    });

    // **MODIFIED** AJAX form submission
    splitExpenseForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(splitExpenseForm);

        fetch(`/tracker/save_split_expense/${friendId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        })
        .then(response => response.json()) // 1. Expect and parse JSON
        .then(data => {
            // 2. Check the status from our JSON response
            if (data.status === 'success' && data.redirect_url) {
                // 3. Redirect the browser using the URL from the server
                window.location.href = data.redirect_url;
            } else {
                // Handle any errors the server might have sent
                alert(data.message || 'An unexpected error occurred.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error saving expense split!');
        });
    });
});