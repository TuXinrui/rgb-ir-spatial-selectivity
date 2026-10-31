#!/usr/bin/env python3
"""Reproduce the paper figures from released RGB-IR measurements.

Inputs are hash-checked JSON/CSV records. Figure 2 is a deterministic schematic.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path as MplPath

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "figures"
BLUE, LIGHT, GREEN, ORANGE = "#245e83", "#8fb8ce", "#517c68", "#b25b3c"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.labelsize": 9, "axes.titlesize": 10, "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5, "legend.fontsize": 8.5,
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#555555", "axes.linewidth": .65,
    "savefig.facecolor": "white", "figure.facecolor": "white",
    "mathtext.fontset": "dejavusans",
})

EXPECTED = {
    "c2former_heads.csv": "56f0c786f2d060909b07c5df3dc7d98a85f46ac61c179a3da820166d778efe0e",
    "cross_dataset_results.json": "d99a91d75378945f5c1027567683643be0737af9b6ce6aaed79ecb1799ad1040",
    "dv_results.json": "366d18692d3c0bd02b0c4e3fc655872345f4535cd2de0d2d98157fe82f76af88",
    "icafusion_heads.csv": "d15660da94ab4e0116798c8063bfcbc6d228ba045dea2e68c59e234cbba32c20"
}

def save(fig, name):
    fig.savefig(OUT / (name + ".pdf"), metadata={"Creator": "RGB-IR spatial selectivity: figure reproduction"})
    fig.savefig(OUT / (name + ".svg"), metadata={"Date": None})
    fig.savefig(OUT / (name + ".png"), dpi=200)
    plt.close(fig)

def metric(level):
    return np.array([level["M"]["mAP50_95_percent"], level["M"]["AP50_percent"]])

def figure1():
    levels = json.loads((DATA / "dv_results.json").read_text(encoding="utf-8"))["levels"]
    points = {}
    for seed in ("s2", "s3"):
        for state in ("uniform", "zero"):
            points[f"ica_{seed}_{state}"] = metric(levels[f"ica_{seed}_{state}"]) - metric(levels[f"ica_{seed}_native"])
    points["c2_L_U"] = metric(levels["c2_L_U"]) - metric(levels["c2_L_N"])
    points["c2_R_U"] = metric(levels["c2_R_U"]) - metric(levels["c2_R_N"])
    points["c2_L_ZERO"] = metric(levels["c2_L_ZERO"]) - metric(levels["c2_L_N"])
    assert sum(len(v) for v in points.values()) == 14
    fig, axes = plt.subplots(1, 3, figsize=(7.14, 3.25),
                             gridspec_kw={"width_ratios": [1.35, 1.13, .74]})
    fig.subplots_adjust(left=.092, right=.985, bottom=.27, top=.74, wspace=.49)
    for ax in axes:
        ax.axhline(0, color="#444444", lw=.8, zorder=2)
        ax.grid(axis="y", color="#dddddd", lw=.55, zorder=0)
        ax.set_axisbelow(True)
    ax = axes[0]
    for i, (seed, color) in enumerate((("s2", BLUE), ("s3", LIGHT))):
        for j, state in enumerate(("uniform", "zero")):
            x = j + (i - .5) * .22
            val = points[f"ica_{seed}_{state}"]
            ax.bar(x, val[0], width=.205, color=color, edgecolor="white", lw=.6, zorder=3)
            ax.scatter(x, val[1], s=28, facecolors="white", edgecolors="#243746", linewidths=1.05, zorder=5)
            if state == "uniform":
                ax.annotate(f"{val[0]:+.4f}", xy=(x, val[0]), xytext=(-16 if i == 0 else 16, 12),
                            textcoords="offset points", ha="center", va="bottom", fontsize=8.5,
                            arrowprops={"arrowstyle": "-", "color": color, "lw": .8},
                            annotation_clip=False)
            else:
                ax.annotate(f"{val[0]:+.4f}", xy=(x,val[0]),
                            xytext=(.70 if i==0 else 1.30,val[0]-.02 if i==0 else val[0]), textcoords="data",
                            ha="right" if i==0 else "left", va="center", fontsize=8.5,
                            arrowprops={"arrowstyle":"-", "color":color, "lw":.7,
                                        "shrinkA":3, "shrinkB":1})
    ax.set(xlim=(-.46, 2.0), ylim=(-.50, .06), xticks=[0, 1], xticklabels=["UNIFORM", "ZERO"],
           ylabel="State − native (pp)")
    ax.legend(handles=[Line2D([0],[0], lw=6, color=BLUE, label="seed 2"),
                       Line2D([0],[0], lw=6, color=LIGHT, label="seed 3")],
              frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(.5, -.20),
              handlelength=.9, columnspacing=1.1)
    ax = axes[1]
    for x, key in enumerate(("c2_L_U", "c2_R_U")):
        val = points[key]
        ax.bar(x, val[0], width=.40, color=GREEN, edgecolor="white", lw=.6, zorder=3)
        ax.scatter(x, val[1], s=30, facecolors="white", edgecolors="#243746", lw=1.1, zorder=5)
        ax.text(x, val[0] - .035, f"{val[0]:+.4f}", ha="center", va="top", fontsize=8.5)
    ax.set(xlim=(-.65, 1.65), ylim=(-.72, .06), xticks=[0,1],
           xticklabels=["L_U\nlearned", "R_U\nreference"], ylabel="State − own native (pp)")
    ax = axes[2]
    val = points["c2_L_ZERO"]
    ax.bar(0, val[0], width=.80, color=ORANGE, edgecolor="white", lw=.6, zorder=3)
    ax.scatter(0, val[1], s=32, facecolors="white", edgecolors="#243746", lw=1.1, zorder=5)
    ax.text(0, val[0] + .67, f"{val[0]:+.4f}", ha="center", va="center", fontsize=8.5,
            color="white",fontweight="bold")
    ax.annotate(f"{val[1]:+.4f}", (0,val[1]), xytext=(8,0), textcoords="offset points",
                ha="left", va="center", fontsize=8.5, annotation_clip=False)
    ax.set(xlim=(-.7,.7), ylim=(-8,.4), xticks=[0], xticklabels=["L_ZERO"], ylabel="L_ZERO − L_N (pp)")
    for panel,title in zip(axes,["(a) ICAFusion","(b) C²Former: uniform","(c) C²Former"]):
        fig.text(panel.get_position().x0,.855,title,fontsize=10,fontweight="bold",va="bottom")
    fig.legend(handles=[Line2D([0],[0],color="#6b7e89",lw=6,label="mAP50–95 (bars)"),
                        Line2D([0],[0],marker="o",mfc="white",mec="#243746",ls="none",label="AP50 (circles)")],
               frameon=False, ncol=2, loc="center", bbox_to_anchor=(.53,.965))
    save(fig, "fig1_results_overview")
    return {k:v.tolist() for k,v in points.items()}

def figure3():
    ica = list(csv.DictReader((DATA / "icafusion_heads.csv").open(encoding="utf-8", newline="")))
    c2 = list(csv.DictReader((DATA / "c2former_heads.csv").open(encoding="utf-8", newline="")))
    assert len(ica) == 96 and len(c2) == 90
    groups = [[], []]
    for seed in ("2", "3"):
        for block in ("25", "26", "27"):
            for branch in ("ir", "vis"):
                rows=[r for r in ica if r["seed"]==seed and r["block"]==f"model.{block}.crosstransformer.0" and r["branch"]==branch]
                assert len(rows)==8
                groups[0].append((f"s{seed}\n{block} {branch}", [float(r["V_S_over_E"]) for r in rows], [float(r["H_S_over_E"]) for r in rows]))
    for stage, n in (("0",3),("1",6),("2",12),("3",24)):
        for direction in ("lwir","vis"):
            rows=[r for r in c2 if r["stage"]==stage and r["direction"]==direction]
            assert len(rows)==n
            groups[1].append((f"stage {stage}\n{direction}", [float(r["V_ratio"]) for r in rows], [float(r["H_ratio"]) for r in rows]))
    fig, axes=plt.subplots(2,1,figsize=(7.14,5.60))
    fig.subplots_adjust(left=.095,right=.985,bottom=.085,top=.86,hspace=.56)
    summaries=[]
    for ai,(ax,gs) in enumerate(zip(axes,groups)):
        for gi,(label,v,h) in enumerate(gs):
            if gi%2==0:ax.axvspan(gi-.48,gi+.48,color="#f3f6f8",zorder=0)
            spread=.25 if ai==0 else .31
            xs=gi+np.linspace(-spread,spread,len(v))
            for x,a,b in zip(xs,v,h):ax.plot([x,x],[b,a],color="#d5dce0",alpha=.7,lw=.45,zorder=1)
            ax.scatter(xs,v,s=6,facecolors="white",edgecolors=BLUE,lw=.6,zorder=3,clip_on=False)
            ax.scatter(xs,h,s=6,marker="s",facecolors="white",edgecolors=ORANGE,lw=.6,zorder=3,clip_on=False)
            for values,color,off in ((v,BLUE,-.46),(h,ORANGE,.46)):
                q1,med,q3=np.percentile(np.asarray(values),[25,50,75])
                summaries.append([float(q1),float(med),float(q3)])
                ax.errorbar(gi+off,med,yerr=[[med-q1],[q3-med]],fmt="_",color=color,
                            capsize=1.8,elinewidth=1.1,markersize=4.2,zorder=5,clip_on=False)
        ax.set_yscale("log");ax.set_ylim(1e-11,1.0)
        ax.set_yticks([1e-11,1e-9,1e-7,1e-5,1e-3,1e-1,1])
        ax.set_xticks(np.arange(len(gs)));ax.set_xticklabels([g[0] for g in gs],fontsize=8.5)
        ax.set_xlim(-.65,len(gs)-.35);ax.set_ylabel("Position-energy ratio")
        ax.grid(axis="y",which="major",color="#d9dfe3",lw=.5,zorder=0)
        ax.get_ygridlines()[-1].set_visible(False)
        ax.set_axisbelow(True)
        ax.set_title(["(a) ICAFusion: 96 heads in 12 groups", "(b) C²Former: 90 heads in 8 groups"][ai],
                     loc="left",fontweight="bold",pad=10)
    fig.legend(handles=[Line2D([0],[0],marker="o",mfc="white",mec=BLUE,ls="none",label="V ratio"),
                        Line2D([0],[0],marker="s",mfc="white",mec=ORANGE,ls="none",label="H = AV ratio"),
                        Line2D([0],[0],marker="_",color="#4b5560",ls="-",label="median / IQR")],
               frameon=False,ncol=3,loc="center",bbox_to_anchor=(.54,.97))
    save(fig,"fig3_native_diagnostics")
    return {"heads": [96,90], "observations":372, "groups":[12,8],"summaries":summaries}

def figure2():
    fig=plt.figure(figsize=(7.14,6.95))
    ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,7.14),ylim=(0,7.40));ax.axis("off")
    colors={"plain":("#f5f7f8","#56616b"),"value":("#eaf2f7",BLUE),
            "uniform":("#fbede6",ORANGE),"retained":("#edf5ed",GREEN)}
    def box(x,y,w,h,text,kind="plain",size=9.0,bold=False):
        fill,edge=colors[kind]
        patch=FancyBboxPatch((x-w/2,y-h/2),w,h,
                            boxstyle="round,pad=0.025,rounding_size=0.04",
                            facecolor=fill,edgecolor=edge,lw=.95)
        ax.add_patch(patch)
        label=ax.text(x,y,text,ha="center",va="center",fontsize=size,
                      fontweight="bold" if bold else "normal",linespacing=1.12)
    def route(points,color="#53616b",dashed=False,head=True):
        path=MplPath(points,[MplPath.MOVETO]+[MplPath.LINETO]*(len(points)-1))
        arrow=FancyArrowPatch(path=path,arrowstyle="-|>" if head else "-",
                              mutation_scale=7.2,lw=.85,color=color,
                              linestyle="--" if dashed else "-",zorder=0)
        ax.add_patch(arrow)
    def note(x,y,text,color="#3f4c55",size=8.5,ha="center",va="center"):
        label=ax.text(x,y,text,fontsize=size,color=color,ha=ha,va=va,linespacing=1.15)
    ax.text(.14,7.25,"(a) ICAFusion: attention and retained output paths",
            fontsize=10,fontweight="bold",va="top")
    ax.text(.14,6.98,"IR direction shown; vis is symmetric. Q/K, current V and residual paths remain.",
            fontsize=8.6,va="top")
    box(.70,6.40,1.08,.50,"RGB tokens\n(pooled + pos)")
    box(.70,5.45,1.08,.50,"IR tokens\n(pooled + pos)")
    box(2.05,6.40,1.12,.50,"LN1\nQ projection","value")
    box(2.05,5.45,1.12,.50,"LN2\nK, V projections","value",8.7)
    box(3.43,6.40,1.08,.50,"QK logits\nsoftmax")
    box(4.79,6.40,1.12,.50,"UNIFORM\n$A\\leftarrow1/n_k$","uniform",9.3,True)
    box(6.17,6.40,1.20,.50,"attention dropout\n$H=A\\cdot V$","value",8.7)
    route([(1.265,6.40),(1.465,6.40)])
    route([(1.265,5.45),(1.465,5.45)])
    route([(2.635,6.40),(2.865,6.40)])
    route([(3.995,6.40),(4.205,6.40)])
    route([(5.375,6.40),(5.545,6.40)])
    # K and V each have a dedicated clear channel below the attention row.
    route([(2.05,5.725),(2.05,5.95),(3.43,5.95),(3.43,6.125)])
    note(2.75,6.02,"K",va="bottom")
    route([(2.635,5.45),(2.78,5.45),(2.78,5.72),(5.95,5.72),(5.95,6.125)],BLUE)
    note(4.55,5.66,"current V",color=BLUE,va="top")
    box(6.17,4.85,1.10,.66,"head concat\nout_proj\nZ")
    box(4.79,4.85,1.20,.76,"output\nsubstitution\nZERO / MEAN\nPERM / CONST",
        "retained",8.6,True)
    box(3.43,4.85,1.15,.66,"gated attention\n+ token residual\nLN2 + MLP",size=8.7)
    route([(6.30,6.125),(6.30,5.205)])
    route([(5.595,4.85),(5.415,4.85)])
    route([(4.165,4.85),(4.03,4.85)])
    box(2.05,4.02,1.55,.56,"Y_IR\nreshape + upsample\nU_IR","retained",8.8)
    # First leave the gated box horizontally, then turn outside its border.
    route([(2.83,4.85),(2.60,4.85),(2.60,4.52),(2.05,4.52),(2.05,4.325)],GREEN)
    box(4.25,4.02,2.04,.54,"new_ir = U_IR + R_IR","retained",9.3,True)
    box(6.25,4.02,1.15,.54,"R_IR\n(retained)","retained")
    route([(2.85,4.02),(3.205,4.02)],GREEN)
    route([(5.65,4.02),(5.295,4.02)],GREEN)

    ax.plot([.14,7.0],[3.60,3.60],color="#d9dfe3",lw=.8)
    ax.text(.14,3.45,"(b) C²Former: sampling and one attention direction",
            fontsize=10,fontweight="bold",va="top")
    ax.text(.14,3.20,"L/R change RGB sampling; IR keeps its reference grid. Sampled IR feeds the other direction.",
            fontsize=8.35,va="top")
    box(.70,2.66,1.08,.62,"RGB features\n(current)")
    box(.70,1.87,1.08,.52,"IR features\n(current)")
    box(2.02,2.26,1.12,.55,"offset predictor\n(RGB + IR)",size=8.7)
    box(3.36,2.66,1.15,.62,"RGB sampler\nL learned\nR reference",size=8.6)
    box(3.36,1.87,1.15,.52,"IR sampler\nreference fixed",size=8.7)
    box(4.72,2.66,1.12,.62,"sampled RGB")
    box(4.72,1.87,1.12,.52,"sampled IR\n(other direction)",size=8.6)
    box(6.10,2.66,1.22,.62,"K, V projections\nfrom sampled RGB","value",8.5)
    route([(1.265,2.66),(2.76,2.66)])
    route([(1.265,1.87),(2.76,1.87)])
    route([(1.265,2.50),(1.435,2.38)])
    route([(1.265,2.00),(1.435,2.14)])
    route([(2.605,2.26),(2.76,2.50)])
    route([(3.96,2.66),(4.135,2.66)])
    route([(3.96,1.87),(4.135,1.87)])
    route([(5.305,2.66),(5.465,2.66)])
    box(1.77,1.12,1.43,.55,"ModalityNorm\n+ Q projection","value",9.0)
    box(3.36,1.12,1.15,.55,"QK logits\nsoftmax")
    box(4.72,1.12,1.12,.55,"N / U\nA or 1/n","uniform",9.4,True)
    box(6.10,1.12,1.12,.55,"dropout\n$A\\cdot V$","value",9.3)
    # A single bus, with no arrowhead at the modality junction.
    route([(.135,2.66),(.055,2.66)],dashed=True,head=False)
    route([(.135,1.87),(.055,1.87)],dashed=True,head=False)
    route([(.055,2.66),(.055,1.12),(1.03,1.12)],dashed=True)
    note(.53,1.36,"current\nRGB + IR",size=8.3)
    route([(2.51,1.12),(2.76,1.12)])
    route([(3.96,1.12),(4.135,1.12)])
    route([(5.305,1.12),(5.515,1.12)])
    # K begins at the projection output; sampled IR remains disconnected from it.
    route([(6.10,2.325),(6.10,2.19),(5.45,2.19),(5.45,1.50),
           (3.36,1.50),(3.36,1.42)])
    note(5.58,1.98,"K",size=8.7,ha="left")
    route([(6.735,2.66),(6.98,2.66),(6.98,1.12),(6.685,1.12)],BLUE)
    note(6.80,1.97,"V",color=BLUE,size=8.7,ha="right")
    box(6.10,.38,1.12,.52,"proj_out\n+ proj_drop")
    box(5.00,.38,.42,.52,"Z",size=10,bold=True)
    box(3.95,.38,1.12,.52,"L_ZERO\n(L only)","retained",9.0,True)
    box(2.53,.38,1.25,.52,"outer 1×1\n+ ReLU")
    box(.92,.38,1.35,.58,"residual add\n→ next stage\n(4 total)","retained",8.8)
    route([(6.10,.82),(6.10,.665)])
    route([(5.515,.38),(5.235,.38)])
    route([(4.765,.38),(4.535,.38)])
    route([(3.365,.38),(3.18,.38)])
    route([(1.88,.38),(1.62,.38)])
    save(fig,"fig2_intervention_site")

def verify_inputs():
    for name, digest in EXPECTED.items():
        if hashlib.sha256((DATA / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"Input checksum mismatch: {name}")
    dv = json.loads((DATA / "dv_results.json").read_text(encoding="utf-8"))
    cross = json.loads((DATA / "cross_dataset_results.json").read_text(encoding="utf-8"))
    if len(dv["levels"]) != 13 or len(dv["contrasts"]) != 10:
        raise SystemExit("Unexpected DroneVehicle record coverage")
    folds = cross["vedai"]["folds"]
    if len(folds) != 10 or any(set(f["states"]) != {"native", "uniform", "zero"} for f in folds.values()):
        raise SystemExit("Expected ten VEDAI folds with three states each")
    counts = {}
    for system, filename, expected in (("ICAFusion", "icafusion_heads.csv", 96),
                                       ("C2Former", "c2former_heads.csv", 90)):
        with (DATA / filename).open(encoding="utf-8", newline="") as stream:
            counts[system] = sum(1 for _ in csv.DictReader(stream))
        if counts[system] != expected:
            raise SystemExit(f"Unexpected head-record count: {filename}")
    return {"dronevehicle_states": 13, "dronevehicle_contrasts": 10,
            "flir_states": 3, "vedai_folds": 10, "vedai_states": 30,
            "native_head_records": counts}


def main(argv=None):
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify input identities and coverage without drawing")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "figures", help="directory for the three PDF/SVG/PNG figures")
    args = parser.parse_args(argv)
    summary = verify_inputs()
    if args.check:
        print(json.dumps(summary, indent=2))
        return
    OUT = args.output_dir.expanduser().resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    figure1()
    figure2()
    f3 = figure3()
    summary.update({"figure1_metric_points": 14, "figure3_observations": f3["observations"],
                    "figure3_groups": f3["groups"], "output_directory": str(OUT),
                    "formats": ["pdf", "svg", "png"]})
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
