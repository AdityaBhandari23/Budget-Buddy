const getIncomeOverTimeData = () => {
  console.log('Calling getIncomeOverTimeData...');
  fetch("/income/total_income_over_time")
     .then((res) => res.json())
     .then((results) => {
          console.log('Received data:', results);
          const months = results.months.sort((a, b) => {
              // Sort months in ascending order (e.g., Jan, Feb, Mar, ...)
              const monthOrder = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
              return monthOrder.indexOf(a) - monthOrder.indexOf(b);
          });
          const totalIncomes = results.total_incomes;

          console.log('Months:', months);
          console.log('Total Incomes:', totalIncomes);

          renderIncomeOverTimeChart(months, totalIncomes);
      })
     .catch((error) => {
          console.error('Error fetching data:', error);
      });
};


// Function to render the income over time chart
const renderIncomeOverTimeChart = (months, totalIncomes) => {
  // Create the chart container
  const chartContainer = document.getElementById('income-over-time-chart');

  // Create the chart
  const chart = new Chart(chartContainer, {
      type: 'line',
      data: {
          labels: months,
          datasets: [{
              label: 'Total Income Over Time',
              data: totalIncomes,
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 1
          }]
      },
      options: {
          title: {
              display: true,
              text: 'Total Income Over Time'
          },
          scales: {
              y: {
                  beginAtZero: true
              }
          }
      }
  });
};

// Call the function to get income over time data
getIncomeOverTimeData();
