from shiny import App, render, ui, reactive, req
from sympy import solve, Eq
from sympy.abc import F, M
from sympy.parsing.sympy_parser import parse_expr
from shiny.ui import h4

# load equations lists

class eqn:
    def __init__(self, name,inline_math, newline_math, variables):
        self.name = name
        self.inline_math = inline_math
        self.newline_math = newline_math
        self.variables = variables

StaticsSumFx = eqn(
    "Equilibrium Forces in X",
    "\(\Sigma F_x=0\)",
    "$$\Sigma F_x=0$$",
    "SigmaFx"
)    

StaticsSumFy = eqn(
    "Equilibrium Forces in Y",
    "\(\Sigma F_y=0\)",
    "$$\Sigma F_y=0$$",
    "SigmaFy"
)    

StaticsSumM = eqn(
    "Equilibrium Moments about O",
    "\(\Sigma M_O=0\)",
    "$$\Sigma M_O=0$$",
    "SigmaM"
)    

StressEqn = eqn(
    "Stress Equation",
    "\(\sigma=\\frac{F}{A}\)",
    "$$\sigma=\\frac{F}{A}$$",
    "sigma,F,A"
)   

AxialDeform = eqn(
    "Axial Deformation by Force",
    "\(\delta_l=\\frac{P L}{AE}\)",
    "$$\delta_l=\\frac{P L}{AE}$$",
    "delta_l,P,L,A,E"
)   

ThermalDeform = eqn(
    "Axial Deformation by Thermal",
    "\(\delta_t= \\alpha \Delta T L\)",
    "$$\delta_t= \\alpha \Delta T L$$",
    "delta_t,alpha,DeltaT,L"
)   

AreaTube = eqn(
    "Area of a Tube",
    "\(A=\pi(r_o^2-r_i^2)\)",
    "$$A=\pi(r_o^2-r_i^2)$$",
    "A,r_o,r_i"
)   
ITube = eqn(
    "Moment of Inertia of a Tube",
    "\(A=\pi(r_o^4-r_i^4)\)",
    "$$A=\pi(r_o^4-r_i^4)$$",
    "A,r_o,r_i"
)   


statics_eqnbank_inline = {
    StaticsSumFx.name : StaticsSumFx.inline_math,
    StaticsSumFy.name : StaticsSumFy.inline_math,
    StaticsSumM.name : StaticsSumM.inline_math,
}
deforms_eqnbank_inline = {
    StressEqn.name : StressEqn.inline_math,
    AxialDeform.name : AxialDeform.inline_math,
    ThermalDeform.name : ThermalDeform.inline_math,
}

geom_eqnbank_inline = {
    AreaTube.name : AreaTube.inline_math,
    ITube.name : ITube.inline_math
}

eqnbank_newline = {
    StaticsSumFx.name : StaticsSumFx.newline_math,
    StaticsSumFy.name : StaticsSumFy.newline_math,
    StaticsSumM.name : StaticsSumM.newline_math,
    StressEqn.name : StressEqn.newline_math,
    AxialDeform.name : AxialDeform.newline_math,
    ThermalDeform.name : ThermalDeform.newline_math,
    AreaTube.name : AreaTube.newline_math,
    ITube.name : ITube.newline_math
}

app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.script(
            src="https://mathjax.rstudio.com/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
        ),
        ui.tags.script(
            "if (window.MathJax) MathJax.Hub.Queue(['Typeset', MathJax.Hub]);"
        ),
    ),
    ui.panel_title("Interactive Problem Solving Environment"),
    ui.layout_sidebar(
        ui.panel_main(
            #ui.markdown("""
            #    <details>
            #        <summary> Click for Answer</summary>
            #            Blah Blah
            #    </details>"""
            #),
            ui.markdown(
                "Your Equation Workspace"
            ),
            ui.output_ui("dyn_eqns"),
            ui.markdown(
                "Use equilibrium equations to find the internal reaction forces:\$$\Sigma F_y=0$$"
            ),
            ui.output_ui("dyn_ui_forces"),
            ui.input_text(
                "forces",
                "Please write the right side of the equation",
                placeholder="Enter math for RHS",
            ),
            ui.markdown(
                "Use equilibrium equeations to find the internal reaction moment:\$$\Sigma M_O=0$$"
            ),
            ui.output_ui("dyn_ui_moments"),
            ui.input_text(
                "moments",
                "Please write the right side of the equation",
                placeholder="Enter math for RHS",
            ),
            ui.output_ui("ui_typeset"),
            ui.input_action_button(
                "typesetMath", "See Updated Equations", class_="btn-secondary"
            ),
            ui.input_action_button(
                "solveEquations", "Solve Equations", class_="btn-success"
            ),
            ui.output_ui("ui_solutions"),
            ui.output_ui("ui_typesetSolutions"),
        ),
        ui.panel_sidebar(
            h4("Equation Bank"),
            ui.navset_tab_card(
                ui.nav(
                    "Statics",
                    ui.input_checkbox_group(
                        "statics_eqns",
                        "Choose which equations you want to use",
                        statics_eqnbank_inline,
                    ),
                ),
                ui.nav(
                    "Strength of Materials",
                    ui.input_checkbox_group(
                        "deforms_eqns",
                        "Choose which equations you want to use",
                        deforms_eqnbank_inline,
                    ),
                ),
                ui.nav(
                    "Geometry",
                    ui.input_checkbox_group(
                        "geom_eqns",
                        "Choose which equations you want to use",
                        geom_eqnbank_inline,
                    ),
                ),
            ),
        ),
    ),
)


def server(input, output, session):
    @output
    @render.ui
    def dyn_ui_forces():
        mystring_forces = "$$ F_y=" + input.forces() + "$$"
        mystring_forces = mystring_forces.replace("*", "\\times")
        return ui.markdown(mystring_forces)

    @output
    @render.ui
    def dyn_ui_moments():
        mystring_moments = "$$ M_O=" + input.moments() + "$$"
        mystring_moments = mystring_moments.replace("*", "\\times")
        return ui.markdown(mystring_moments)

    @output
    @render.ui
    @reactive.event(input.typesetMath, ignore_none=False)
    def ui_typeset():
        return ui.tags.script(
            "if (window.MathJax) MathJax.Hub.Queue(['Typeset', MathJax.Hub]);"
        )

    @output
    @render.ui
    @reactive.event(input.solveEquations, ignore_none=False)
    def ui_solutions():
        solvedForces = solve(Eq(F, parse_expr(input.forces())), F)
        solvedMoments = solve(Eq(M, parse_expr(input.moments())), M)
        mystring_solvedForces = "$$ F_O=" + str(solvedForces[0]) + "$$"
        mystring_solvedMoments = "$$ M_O=" + str(solvedMoments[0]) + "$$"
        return ui.markdown(mystring_solvedForces), ui.markdown(mystring_solvedMoments)

    @output
    @render.ui
    @reactive.event(input.solveEquations, ignore_none=False)
    def ui_typesetSolutions():
        return ui.tags.script(
            "if (window.MathJax) MathJax.Hub.Queue(['Typeset', MathJax.Hub]);"
        )

    @output
    @render.ui
    def dyn_eqns():
        eqns_keys = input.statics_eqns()+input.deforms_eqns()+input.geom_eqns()
        req(eqns_keys)
        lookup_eqns=[eqnbank_newline[key] for key in eqns_keys]
        
        mystring_eqns = str(lookup_eqns)

        return [ui.panel_well(ui.markdown(mystring_eqns),
                ui.tags.script("if (window.MathJax) MathJax.Hub.Queue(['Typeset', MathJax.Hub]);"))]

    
    #@output
    #@render.ui
    #def dyn_ui_forces():
    #    mystring_forces = "$$ F_y=" + input.forces() + "$$"
    #    mystring_forces = mystring_forces.replace("*", "\\times")
    #    return ui.markdown(mystring_forces)


app = App(app_ui, server)
