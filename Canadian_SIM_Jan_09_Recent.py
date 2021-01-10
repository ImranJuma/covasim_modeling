'''
Canadian scenarios for evaluating effectivness of masks
'''
import sciris as sc
import covasim as cv
import pylab as pl
import numpy as np
import argparse
import os
pl.switch_backend('agg')

# Check version
cv.check_version('2.0.0') #Use This To Keep COVASIM updated to always run the newest version 
cv.git_info('covasim_version.json')

do_plot = 1
do_save = 1
do_show = 1
verbose = 1
seed    = 1

scenario = ['Scenario_1_Normal', 'Senario_2_0_COMP'][1] #These are the different simulation running 
tti_scen = ['current'][0] #Sticking With Current At The Moment 

version   = 'v1'
date      = '2020june17'
folder    = f'results_FINAL_{date}'
file_path = f'{folder}/phase_{version}' 
data_path = 'Data_Feed_File.xlsx' #Here is our data file  
fig_path  = f'{file_path}_{scenario}.png'

start_day = '2020-01-21' #Begining Date For Simulation
end_day   = '2021-12-31' #Ending Date For Simulation

# Set the parameters
total_pop    = 37.42e6 # Current Canadian population size
pop_size     = 100e3 # Actual simulated population 
pop_scale    = int(total_pop/pop_size)
pop_type     = 'hybrid' #Recall what this was, and we can adapt accordingly 
pop_infected = 1500 #Starting With An Estimated Infected Population Of 1500
beta         = 0.00467
asymp_factor = 2 #Need To Paramatize 
contacts     = {'h':3.0, 's':20, 'w':20, 'c':20} #Need To Paramatize 

pars = sc.objdict(
    pop_size     = pop_size,
    pop_infected = pop_infected,
    pop_scale    = pop_scale,
    pop_type     = pop_type,
    start_day    = start_day,
    end_day      = end_day,
    beta         = beta,
    asymp_factor = asymp_factor,
    contacts     = contacts,
    rescale      = True,
)

# Create the baseline simulation
sim = cv.Sim(pars=pars, datafile=data_path, location='Canada') #Setting the country to where we want the SIM to occure 
sim['prognoses']['sus_ORs'][2] = 1.0 # ages 0-10 #Let's suggest for this simulation that kids are more susptible 
sim['prognoses']['sus_ORs'][1] = 1.0 # ages 10-20


#%% Interventions
#These dates have been imprted to account for scenarios that will occure effecting posotive ^ or down cases of COVID-19
tc_day = sim.day('2020-03-05') #intervention of some testing (tc) starts on 16th March and we run until 1st April when it increases
te_day = sim.day('2020-04-05') #intervention of some testing (te) starts on 1st April and we run until 1st May when it increases
tt_day = sim.day('2020-05-05') #intervention of increased testing (tt) starts on 1st May
tti_day= sim.day('2020-07-01') #intervention of tracing and enhanced testing (tti) starts on 1st June / https://toronto.ctvnews.ca/where-is-the-covid-19-contact-tracing-app-that-was-supposed-to-launch-in-ontario-1.5031527#:~:text=The%20federally%2Dbacked%20COVID%20Alert,before%20launching%20the%20program%20nationwide.
ti_day = sim.day('2021-12-20') #schools interventions end date in December 2021
tti_day_july= sim.day('2020-08-01') #intervention of tracing and enhanced testing (tti) at different levels starts on 1st August  #Close to end of the month
tti_day_august= sim.day('2020-09-01') #intervention of tracing and enhanced testing (tti) at different levels starts on 1st August #


#Various Intervention Dates that will have a increase or decrease in overall transmission. 
#FORMAT = [YYYY-MM-DD]
#What is the scale of these kinds of values 
beta_days = ['2020-02-14',  '2020-03-20', '2020-04-17', '2020-07-17', '2020-08-26', '2020-09-04', '2020-10-16', '2020-11-06', '2020-12-26',  '2021-01-11', 
'2021-03-21', '2021-07-04', '2021-09-01', ti_day]


# Fully Schools from Sep opening with society opening
# Phased opening with society opening and masks effective coverage=15% from 24th July
# masks in schools from 1st September
if scenario == 'Scenario_1_Normal':
    h_beta_changes = [0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.80, 0.50, 0.50, 0.50, 0.50]
    s_beta_changes = [0.80, 0.70, 0.50, 0.80, 0.70, 0.50, 0.80, 0.70, 0.50, 0.80, 0.70, 0.50, 0.80, 0.50]
    w_beta_changes = [0.80, 0.70, 0.50, 0.80, 0.70, 0.50, 0.80, 0.70, 0.50, 0.80, 0.70, 0.50, 0.80, 0.50]
    c_beta_changes = [0.80, 0.70, 0.50, 0.80, 0.70, 0.50, 0.80, 0.70, 0.50, 0.80, 0.70, 0.50, 0.80, 0.50]

#Phased opening with society opening and masks effective coverage=30% from 24th July
# masks in schools from 1st September
elif scenario == 'Senario_2_0_COMP':
    h_beta_changes = [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00]
    s_beta_changes = [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00]
    w_beta_changes = [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00]
    c_beta_changes = [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00]   

else:
    print(f'Scenario {scenario} not recognised')


#---------------------------------------------------------------------------------------------------------#
#Everything Below This Line Should Be Done In Callibration After Above Is First Completed

# Define the beta changes
h_beta = cv.change_beta(days=beta_days, changes=h_beta_changes, layers='h')
s_beta = cv.change_beta(days=beta_days, changes=s_beta_changes, layers='s')
w_beta = cv.change_beta(days=beta_days, changes=w_beta_changes, layers='w')
c_beta = cv.change_beta(days=beta_days, changes=c_beta_changes, layers='c')

#next line to save the intervention
interventions = [h_beta, w_beta, s_beta, c_beta]

if tti_scen == 'current':

    # Tracing and enhanced testing strategy of symptimatics from 1st June
    #testing in June remains the same as before June under this scenario
    s_prob_march = 0.012
    s_prob_april = 0.012
    s_prob_may   = 0.0165
    s_prob_june = 0.0171
    s_prob_july = 0.0171
    s_prob_august = 0.0171
    t_delay       = 1.0

    iso_vals = [{k:0.1 for k in 'hswc'}]

    #tracing level at 50% in June; 60 in December
    t_eff_june   = 0.50
    t_eff_july   = 0.50
    t_eff_aug   = 0.60
    t_eff_sept   = 0.65
    t_eff_oct   = 0.70
    t_eff_nov   = 0.60
    t_eff_dec   = 0.60
    t_probs_june = {k:t_eff_june for k in 'hwsc'}
    t_probs_july = {k:t_eff_july for k in 'hwsc'}
    t_probs_aug = {k:t_eff_july for k in 'hwsc'}
    t_probs_sept = {k:t_eff_july for k in 'hwsc'}
    t_probs_oct = {k:t_eff_july for k in 'hwsc'}
    t_probs_nov = {k:t_eff_july for k in 'hwsc'}
    t_probs_dec= {k:t_eff_july for k in 'hwsc'}
    
    trace_d_1      = {'h':0, 's':1, 'w':1, 'c':2}

    #testing and isolation intervention
    interventions += [
        cv.test_prob(symp_prob=0.009, asymp_prob=0.0, symp_quar_prob=0.0, asymp_quar_prob=0.0, start_day=tc_day, end_day=te_day-1, test_delay=t_delay),
        cv.test_prob(symp_prob=s_prob_april, asymp_prob=0.0, symp_quar_prob=0.0, asymp_quar_prob=0.0, start_day=te_day, end_day=tt_day-1, test_delay=t_delay),
        cv.test_prob(symp_prob=s_prob_may, asymp_prob=0.00075, symp_quar_prob=0.0, asymp_quar_prob=0.0, start_day=tt_day, end_day=tti_day-1, test_delay=t_delay),
        cv.test_prob(symp_prob=s_prob_june, asymp_prob=0.00075, symp_quar_prob=0.0, asymp_quar_prob=0.0, start_day=tti_day, end_day=tti_day_july-1, test_delay=t_delay),
        cv.test_prob(symp_prob=s_prob_july, asymp_prob=0.00075, symp_quar_prob=0.0, asymp_quar_prob=0.0, start_day=tti_day_july, end_day=tti_day_august-1, test_delay=t_delay),
        cv.test_prob(symp_prob=s_prob_august, asymp_prob=0.00075, symp_quar_prob=0.0, asymp_quar_prob=0.0, start_day=tti_day_august, test_delay=t_delay),
        cv.dynamic_pars({'iso_factor': {'days': te_day, 'vals': iso_vals}}),
        cv.contact_tracing(trace_probs=t_probs_june, trace_time=trace_d_1, start_day=tti_day, end_day=tti_day_july-1),
        cv.contact_tracing(trace_probs=t_probs_july, trace_time=trace_d_1, start_day=tti_day_july),
      ]

else:
    print(f'Scenario {tti_scen} not recognised')


# Finally, update the parameters
sim.update_pars(interventions=interventions)
for intervention in sim['interventions']:
    intervention.do_plot = False

if __name__ == '__main__':

    noise = 0.00

    msim = cv.MultiSim(base_sim=sim) # Create using your existing sim as the base
    msim.run(reseed=True, noise=noise, n_runs=12, keep_people=True) # Run with uncertainty

    save_dir = os.getcwd()

    # Recalculate R_eff with a larger window
    for sim in msim.sims:
        sim.compute_r_eff(smoothing=10)

    print('------- IMRANS EXPORT TO XLS CODE -------')
    # Export simulation results to xls
    for sim in msim.sims:
        sim_label = sim.label.replace(" ","")
        xls_filepath = f"{save_dir}/{sim_label}_exported_results"
        print('exporting xls to:', xls_filepath)
        try: 
            sim.to_excel(xls_filepath)
            print(' >   export sucessful!')
        except: 
            print(' > export failed for unknown reason...')
    print('------- COMPLETED EXPORT XLS CODE -------')
    
    msim.reduce() # "Reduce" the sims into the statistical representation

    #to produce mean cumulative infections and deaths for barchart figure
    print('Mean cumulative values:')
    print('Deaths: ',     msim.results['cum_deaths'][-1])
    print('Infections: ', msim.results['cum_infections'][-1])

    try:
        os.makedirs("%s" % scenario)
    except:
        pass
    outfile = "%s/test%s-trace%s.obj" % (scenario, args.test, args.trace)
    sc.saveobj(outfile, sc.objdict((("args", args), ("results", msim.results))))

    # Save the key figures
    plot_customizations = dict(
        interval   = 90, # Number of days between tick marks
        dateformat = '%m/%Y', # Date format for ticks
        fig_args   = {'figsize':(14,8)}, # Size of the figure (x and y)
        axis_args  = {'left':0.15}, # Space on left side of plot
        )

    msim.plot_result('r_eff', **plot_customizations)
    #sim.plot_result('r_eff')
    pl.axhline(1.0, linestyle='--', c=[0.8,0.4,0.4], alpha=0.8, lw=4) # Add a line for the R_eff = 1 cutoff
    pl.title('')
    pl.savefig('%s/test%s-trace%s-R.pdf' % (scenario, args.test, args.trace))


    #Imran: To Populate The Reults In A Exported XLXS File For Us To Review
    print('---------- EXPORT XLXS ------------ ')
    print('cum_deaths:', **plot_customizations)
    print('---------- EXPORT XLXS ------------ ')
    msim.plot_result('cum_deaths', **plot_customizations)
    pl.title('')
    cv.savefig('%s/test%s-trace%s-Deaths.pdf' % (scenario, args.test, args.trace))

    msim.plot_result('new_infections', **plot_customizations)
    pl.title('')
    cv.savefig('%s/test%s-trace%s-Infections.pdf' % (scenario, args.test, args.trace))

    msim.plot_result('cum_diagnoses', **plot_customizations)
    pl.title('')
    cv.savefig('%s/test%s-trace%s-Diagnoses.pdf' % (scenario, args.test, args.trace))

