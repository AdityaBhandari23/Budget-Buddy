const renderTopSourcesChart = (labels, data) => {
  var ctx = document.getElementById("myBarChart").getContext("2d");
  var myBarChart = new Chart(ctx, {
      type: "bar",
      data: {
          labels: labels,
          datasets: [
              {
                  label: "Top Sources of Income",
                  data: data,
                  backgroundColor: [
                      "rgba(255, 99, 132, 0.2)",
                      "rgba(54, 162, 235, 0.2)",
                      "rgba(255, 206, 86, 0.2)",
                      "rgba(75, 192, 192, 0.2)",
                      "rgba(153, 102, 255, 0.2)",
                  ],
                  borderColor: [
                      "rgba(255, 99, 132, 1)",
                      "rgba(54, 162, 235, 1)",
                      "rgba(255, 206, 86, 1)",
                      "rgba(75, 192, 192, 1)",
                      "rgba(153, 102, 255, 1)",
                  ],
                  borderWidth: 1,
              },
          ],
      },
      options: {
          title: {
              display: true,
              text: "Top Sources of Income",
          },
      },
  });
};

const getTopSourcesData = () => {
  fetch("/income/top_sources_summary")
      .then((res) => res.json())
      .then((results) => {
          const top_sources = results.top_sources;
          const top_amounts = results.top_amounts;

          renderTopSourcesChart(top_sources, top_amounts);
      });
};

document.onload = getTopSourcesData();

