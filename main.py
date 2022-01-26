import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

nations = ["Argentina",
"Australia",
"Brazil",
"Canada",
"France",
"Germany",
"Japan",
"India",
"Indonesia",
"Italy",
"Mexico",
"Russia",
"South Africa",
"Saudi Arabia",
"South Korea",
"Turkey",
"United Kingdom",
"United States",
"Spain",
"Sweden",
"Croatia",
"Hungary",
"Belgium",
"Portugal",
"Norway",
"Colombia",
"Chile",
"Denmark",
"Austria",
"Morocco"]

#European nations
# nations = ['Austria', 'Belgium', 'Croatia', 'Denmark', 'France', 'Germany', 'Hungary', 'Italy', 'Norway', 'Portugal', 'Spain', 'Sweden','United Kingdom']
nations.sort()
# Upload the data taken from https://ourworldindata.org/covid-cases updated to 2021-12-24
dataset = pd.read_csv("./owid-covid-data.csv")
all_distances = []

# Dictionary for the peaks of all nations
peaks_dict = {}
for nat in nations:
    peaks_dict[nat] = []

# Function to extract the columns of interest from the dataset ('date','new_cases')
def convert_df(data, x, y, nation):
    df = data[data["location"] == nation]
    df = [df[x], df[y]]
    headers = ["x", "y"]
    filtered_data = pd.concat(df, axis=1, keys=headers)
    filtered_data.x = pd.to_datetime(filtered_data.x)
    filtered_data = filtered_data.sort_values("x")
    # replacing NaN data with the value 0.0
    filtered_data["y"] = filtered_data["y"].fillna(0.0)

    #Computing a 7-day rolling average
    filtered_data["y"] = filtered_data["y"].rolling(7).mean()
    filtered_data["y"] = filtered_data["y"].fillna(0.0)
    return filtered_data

# Function that checks if the candidate peak is greater than the number of daily SARS-COV-2 cases
# reported in the 28 days both before and after n. (where n is the position of the peak in the dataset)
def check_real_peak(wave_period, candidate_peak):
    for n in wave_period:
        if n > candidate_peak:
            return False
    return True



# Function that returns the list of identified peaks
# We considered a peak has happened in a given day n, if the number of SARS-COV-2 infections
# registered in that day was larger than the number of daily SARS-COV-2 cases reported in the 28 days
# both before and after n. Not only, but to be considered a peak, the number of infections registered
# on that day n had to be larger than a given threshold computed as the 84 % of the average
# of the daily cases reported in all the days since the beginning of the pandemic until n
def find_peaks(df,nat):
    relevant_peaks = []
    check_length = 28
    y = df["y"].values
    length = len(y)
    i = 1
    while i < length-1:
        if (y[i] >= y[i-1]) and (y[i] > y[i+1]) and (i >= check_length) and (i+check_length < length):
            if check_real_peak(np.concatenate([y[i-check_length:i],y[i+1: i+check_length+1]]), y[i]):
                threshold = np.mean(y[:i]) * 84 / 100
                if y[i] > threshold:
                    relevant_peaks.append( (i,y[i]) ) # Each element of the list is a pair formed by the position of the peak in the dataset and by the corresponding number of infections
                    peaks_dict[nat].append(df['x'].values[i])
                i += check_length
        i += 1
    return relevant_peaks

# Custom output
def output(first_peak, second_peak):
    distance = second_peak - first_peak
    second_peak = second_peak.strftime("%Y/%m/%d")
    first_peak = first_peak.strftime("%Y/%m/%d")
    n_days = distance.days
    all_distances.append(n_days)
    print("First highest peak : " + str(first_peak), "\t", "Second highest peak: " + str(second_peak), "\t", "Distance in days: " + str(n_days))

# Function that returns the positions of the two highest peaks
def find_max(list_of_peaks):
    first_max = 0
    second_max = 0
    index_1 = 0
    index_2 = 0
    for peak in list_of_peaks:
        if peak[1] >= first_max:
            second_max = first_max
            index_2 = index_1
            first_max = peak[1]
            index_1 = peak[0]
        elif second_max<peak[1]<first_max:
            second_max = peak[1]
            index_2 = peak[0]
    res = [index_1,index_2]
    res.sort()
    return res

for nat in nations:
    df = convert_df(dataset, "date", "new_cases", nat)
    df = df.reset_index(drop=True)
    print(nat, ":")
    peaks = find_peaks(df,nat)
    print('Number of peaks','->',len(peaks))
    indexes = []
    if len(peaks) >= 2:
        indexes = find_max(peaks)
        first_peak_date = df["x"][indexes[0]] # Date of the first peak
        second_peak_date = df["x"][indexes[1]] # Date of the second peak
        output(first_peak_date,second_peak_date)

    print(np.datetime_as_string(peaks_dict[nat], unit='D'))
    print()

    # Plotting the time series of new infections
    df.x = df.x.dt.strftime("%Y/%m/%d")
    df.plot(
        y="y",
        x="x",
        title=nat,
        style= ".-",
        xlabel="Date",
        ylabel="New Cases"
    )

    # Plotting vertical lines corresponding to the dates of the peaks
    for index in indexes:
        plt.axvline(x = index, color = "red", linewidth = 1.15)

    plt.legend(["New Cases","Peak"])
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

print("Average of the distances between the two highest peaks of all nations: ", np.mean(all_distances))
print("Variance of the distances between the two highest peaks of all nations: ", np.var(all_distances))
print("Standard deviation of the distances between the two highest peaks of all nations: ", np.std(all_distances))

