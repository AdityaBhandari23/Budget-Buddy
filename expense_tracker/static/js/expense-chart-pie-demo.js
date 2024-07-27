const getExpenseOverTimeData = () => {
    console.log('Calling getExpenseOverTimeData...');
    fetch("/total_expense_over_time")
       .then((res) => res.json())
       .then((results) => {
            console.log('Received data:', results);
            const months = results.months.sort((a, b) => {
                // Sort months in ascending order (e.g., Jan, Feb, Mar, ...)
                const monthOrder = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                return monthOrder.indexOf(a) - monthOrder.indexOf(b);
            });
            const totalExpenses = results.total_expenses;
  
            console.log('Months:', months);
            console.log('Total Expenses:', totalExpenses);
  
            renderExpenseOverTimeChart(months, totalExpenses);
        })
       .catch((error) => {
            console.error('Error fetching data:', error);
        });
  };
  
  
  // Function to render the expense over time chart
  const renderExpenseOverTimeChart = (months, totalExpenses) => {
    // Create the chart container
    const chartContainer = document.getElementById('expense-over-time-chart');
  
    // Create the chart
    const chart = new Chart(chartContainer, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Total Expense Over Time',
                data: totalExpenses,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            title: {
                display: true,
                text: 'Total Expense Over Time'
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
  };
  
  // Call the function to get expense over time data
  getExpenseOverTimeData();
  
  
 