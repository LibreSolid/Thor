<h1 align="center">
 <a href="http://thor.angel-lm.com">
    <picture>
      <source height="80" media="(prefers-color-scheme: dark)" srcset="doc/logo_dark.svg">
      <img height="80" alt="Fiber" src="doc/logo_light.svg">
    </picture>
  </a>

 <br>

 <a href="http://thor.angel-lm.com/">
     <img src="https://img.shields.io/badge/website-thor.angel--lm.com-red?logo=htmx">
 </a>
 <a href="http://thor.angel-lm.com/worldwide/">
     <img src="https://img.shields.io/endpoint?url=https://angel-lm.com/thor/thor-counter.php">
 </a>
 <a href="http://thor.angel-lm.com/forums/">
     <img src="https://img.shields.io/endpoint?url=https://angel-lm.com/thor/forum-counter.php&color=orange">
 </a>
 <a href="https://discord.com/invite/a5dSVqSUK5">
     <img src="https://img.shields.io/discord/1189278202514907166?label=discord&logo=discord">
 </a>
 <a href="https://creativecommons.org/licenses/by-sa/4.0/legalcode">
     <img src="https://img.shields.io/github/license/angellm/Thor">
 </a>
</h1>
<p align="center">
 <em><b>Thor</b> is an open source, 3D printed, 6 degrees of freedom robotic arm. Designed to be affordable and accessible, Thor is ideal for educational settings, makers, and robotics enthusiasts. With a height of 625mm it has the capacity to lift up to 750g. Its yaw-roll-roll-yaw-roll-yaw configuration is common in industrial manipulators.</em>
</p>
<p align="center">
 <img src="doc/banner.png" width="800">
</p>

## ✨ Key Features

- 🧩 **Born Open Source**: Designed using open source software such as FreeCAD, KiCAD, GRBL, RRF and ROS.
- 🕊️ **Released Open Source**: All source files published under CC-BY-SA-4.0 license.
- 💰 **Low Cost**: Hardware cost below 350€.
- 📚  **Suitable for education**: Perfect for robotics courses in schools and universities, there are already success cases!
- 🧰 **G-code Controlled**: Uses the same language as 3d printers and CNCs to move.
- 🐳 **ROS2 Integration**: Available implementation using Docker for flexibility.


## 📦 Repository Structure
- `freecad-src` – Source files of 3D models created with FreeCAD
- `mods` – Modified models and improvements to standard models
- `stl` – Printable STL files
- `step` – STEP files


## 🔗 Related Repositories
- [**Thor-ROS**](https://github.com/AngelLM/Thor-ROS): ROS2 & Moveit2 configuration files and packages to work with Thor.
- [**ThorControlPCB**](https://github.com/AngelLM/ThorControlPCB): Source & manufacture files of Arduino Mega shield designed to control Thor.
- [**Asgard**](https://github.com/AngelLM/Asgard): Control software for thor motors with a simple interface.



## 🚀 Getting Started

1. **Read the Documentation**: Comprehensive guides on printing, assembly, electronics, and firmware are available at [thor.angel-lm.com/documentation](http://thor.angel-lm.com/documentation/).
2. **Print the Parts**: Use the STL files in this repository.
3. **Get the Hardware**: Take a look to the [Bill of Materials](http://thor.angel-lm.com/documentation/bom/).
4. **Assemble the Robot**: See [here](http://thor.angel-lm.com/documentation/assembly/) for assembly videos and interactive instructions. 
5. **Assemble & Setup the Electronics**: The [Wiring & Setup](http://thor.angel-lm.com/documentation/electronics/) guide will help you prepare your electronic board and make the hardware connections. 
6. **Install the Firmware**: Depending on which electronics you have chosen, you will have to perform a different firmware configuration. [This page](http://thor.angel-lm.com/documentation/firmware/) explains the steps to follow.
7. **Control the Robot**: Use Asgard to move the robot. [Here](http://thor.angel-lm.com/documentation/control-software/) is how to do it.



## 🧠 Technical Specifications

- **Degrees of Freedom**: 6 (yaw-roll-roll-yaw-roll-yaw).
- **Height Stretched**: 625mm (without end effector).
- **Payload Capacity**: 750g max (including end effector weight).
- **Motors**: Stepper motors.
- **Electronics**: DIY PCB or commercial boards.
- **Transmission**: 3D printed gears, GT2 pulleys and belts.
- **Software**: FreeCAD, KiCAD, GRBL, RRF, ROS2.



## 📚 Additional Resources

- 🌐 **Official Website**: [thor.angel-lm.com](http://thor.angel-lm.com/)
- ❓ **Frequently Asked Questions**: [FAQ](http://thor.angel-lm.com/faq/)
- 💬 **Thor Community Forums**: [Thor Forums](http://thor.angel-lm.com/forums/)
- 💬 **Thor Discord Server**: [Thor Robot Community](https://discord.com/invite/a5dSVqSUK5)



## 🤝 Contributing

Contributions are welcome! If you'd like to improve Thor — whether it's design, documentation, or code — feel free to open an [Issue](https://github.com/AngelLM/Thor/issues) or submit a Pull Request.



## 🤖 Simulation

This repository also carries a **solid-node** simulation layer under
`simulation/`: the whole machine assembled from its own published parts, six
joints and a gripper a maker can drive in a browser, and contracts that fail
when an interface stops holding. Nothing under `stl/`, `step/`,
`freecad-src/`, `mods/` or `doc/` is edited by it — the printed parts are
read from `step/*.step` as they are, and every placement comes from the
FreeCAD Assembly4 documents' own solved values.

### Running it

With `solid-node` installed:

```bash
solid build                       # build once and publish the model
solid develop                     # a live viewer that rebuilds on save
solid test --exact simulation/thor.py     # the contracts
solid snapshot -o thor.png --autocenter --viewall
```

The contracts run on the **exact** kernel and only on it. Seven of Thor's
printed parts tessellate to a mesh that is not closed at the default
deflection — their solids are sound — and the faceted kernel refuses those
meshes rather than answering, so `--faceted` cannot run this machine.

### What the sliders mean

| driver | what it measures | range |
| --- | --- | --- |
| `art1` | the base's yaw about Z | ±180° |
| `art2` | the shoulder's roll about Y, 202.0 mm up | ±90° |
| `art3` | the elbow's roll, **relative to the upper arm** | ±135° |
| `art4` | the forearm's yaw about its own axis | ±180° |
| `art5` | the wrist's roll about Y, 556.0 mm up | ±105° |
| `art6` | the tool's roll about the wrist output axis | ±180° |
| `grip` | the clear opening between the two jaws | 0–69.94 mm |

Each of the seven is one joint: move one slider and one joint moves. `art3`
used to be stated as the forearm's roll in the machine frame, on the
argument that the elbow's drive pulley is carried by the shoulder housing
rather than by the arm, so a shoulder swing would leave the forearm
pointing where it was. That is true only for equal pulleys, and Thor's are
not: the drive pulley has twenty teeth and the elbow pulley a hundred and
seventeen, so with the motor still a swing of θ turns the forearm against
the arm by −20 θ / 117, not by −θ. The earlier reading was wrong, and the
model no longer makes it.

The coupling is still there, and it is the motor's problem. `Art1` states
what its elbow motor must turn, `shoulder + (117/20) · elbow`, which is the
compensation a controller makes; swing `art2` alone and that motor turns.
The published joint
limits are not in this repository, so the ranges above are the mechanism's
own travel where the geometry bounds it and the full circle otherwise;
they are presentation only and clamp nothing.

### How the model moves

Every freedom of the machine is declared where the body that has it lives,
as a `Revolute` joint stating the axis and the anchor **in the frame its
parent places it in** — the base's yaw on `Art1`, the shoulder on `Art2`,
the elbow on `Art3`, the forearm's yaw on `Art4`, the wrist on `Art56`, the
tool roll on `WristOutput`. The framework carries each line into the moving
part's own coordinates, so nothing here computes a pivot by hand: the
elbow, whose axis sits 81.5 mm from the forearm's own origin, is one
declaration rather than a translate–rotate–translate sandwich.

The seven drivers reach those joints by **path**, from the root:

```python
art2.drives(shoulder.art2.shoulder)
art5.drives(shoulder.art2.art3.art4.art56.wrist)
```

so no sub-assembly declares a port merely to hand a value to the one below
it. Two of the relations are not that simple, and both are the mechanism
talking:

- The elbow's motor sits on the shoulder housing, so the belt sees its
  pulley only against the arm. `Art1` declares what that pulley turns
  relative to the housing, `art2.shoulder + (117/20) · art2.art3.elbow`,
  and drives the pulley, its optical disc and the motor from it. The
  pulley then turns `drive − shoulder` against the arm, the belt carries
  20/117 of that onto the elbow pulley, and what comes out is the elbow
  angle the maker asked for.
- The wrist is a differential, so each of its two motors turns for either
  joint: `Art4` declares `wrist ± 2 · tool` and drives the motors and the
  two belts from those.

Gearing is a `ratio=` on the relation and belt travel is the pitch arc, so
each motor and each belt is one line beside the pair it belongs to.

#### What still turns by hand

Five `simulate()` methods survive, and each does one thing: turn the
printed gears, pulleys, optical discs and the ball cage that spin on their
own bearings. A joint would say this better, but a joint's axis and anchor
are resolved when the node is constructed, and a part placed by
`place_from_design` only learns where it stands when its parent renders —
so a joint cannot yet be anchored at a design-placed part's own origin.
The gripper keeps its own kinematics too: its jaws are the couplers of a
parallelogram and translate on a circle, which is not one lower pair.

The instructions are `Home`, `Ready`, `Reach`, `Pick`, `Place` and `Park`.
A scenario contract triggers all six in order, at the rate each joint's own
mechanism allows, and asks the machine on the way whether it has driven any
part through another.

### Looking at it in pieces

Each sub-assembly builds on its own, in the order the robot stands up:

```bash
solid build simulation/base.py:Base       # the plinth and the electronics box
solid build simulation/art1.py:Art1       # the shoulder housing and up
solid build simulation/art2.py:Art2       # the upper arm and up
solid build simulation/art3.py:Art3       # the elbow's output link and up
solid build simulation/art4.py:Art4       # the forearm and the wrist
solid build simulation/art56.py:Art56     # the wrist differential and gripper
solid build simulation/gripper.py:Gripper # the end effector alone
```

### What the model found in the design

Assembling Thor in software is the first time anything has asked its files
every question at once, and some of the answers are worth having. All of
these are measured; `docs/measurements.md` carries the numbers and how they
were read, and none of them is fixed upstream.

- **The elbow-to-wrist span is 194.0 mm, not the 195.00 the axis drawing
  states.** The drawing's other two spans, 202.00 and 160.00, match the
  assembly exactly.
- **No gear pair in the assembly is phased to mesh.** All five printed
  pairs interpenetrate at the pose the assembly records, by 0.2 to
  46.2 mm³. A builder puts a pinion on at an angle that drops into mesh;
  the model measures that angle for each pair.
- **The two shoulder pinions need different angles** — 31.5° and 19.5° —
  although the design places them symmetrically. They are mirrored
  instances of one part.
- **The base pinion has no interference-free angle at all.** It stands
  2 mm taller than the ring gear it drives, and its top rim cuts the rim
  above the teeth by 0.20 mm³ whatever angle it is put on.
- **The forearm pinion's lower flange fouls the column's gear** by
  24.30 mm³ at every angle: the flange is 1.2 mm larger in radius than the
  teeth, and the ring at the foot of the column's gear is not relieved for
  it.
- **The arm's two sprung tensioners do not reach its belt.** The taut run
  between the shoulder and elbow pulleys passes 5.41 mm clear of their
  rims, so they are drawn retracted and the belt is a plain two-pulley
  loop of 462.98 mm — 231.5 teeth, which is what the tensioners are there
  to take up.
- **The arm's two belt pulleys share only 3.65 mm of land for a 6 mm
  belt.** Their running surfaces overlap between 18.000 and 21.651 along
  the shoulder axis and nowhere else. The forearm's pulleys share their
  whole 7.5 mm land, which is how you know this one is the arm's.
- **The forearm belts are named for 208 mm and their pulleys need
  223.5 mm.** The design's own belt solid measures about 220, so it is the
  name that is wrong — but a builder buying by the name gets a belt that
  will not close.
- **All three belt solids are placed where their pulleys are not.** Both
  forearm belts lie flat in a plane perpendicular to their pulleys' axes,
  and the arm's belt clears both of its own pulleys.
- **`Art1Top` is one solid that tessellates into five bodies** — the part,
  three zero-volume patches and a detached lug — which is why every
  question here is asked of the solids.
- **The wrist's belt pulleys are 4 mm-bore pulleys on a 5 mm shaft.** The
  design's own `GT2x40PulleyM4` is bored 2.000 in radius and its own
  `Shaft_5x102mm` is 2.500, so half a millimetre of bore wall is solid
  shaft over the pulley's whole 17 mm.

The interference contract that finds these is **red on purpose**: 272
pairs of solids share space at the home pose and thirteen are recorded, so
the model is still telling the truth about how much it has explained.
`docs/measurements.md` breaks the rest down.
- **`GripperBot` is sunk 3248.9 mm³ into `Art56GearPlate`.** The gripper
  base's mounting boss occupies the same space as the plate it bolts to;
  neither part rebates for the other.
- **`Art4Optodisk` passes 24.1 mm³ through `Art3Body`'s wall** rather than
  running in a slot cut for it.
- **`Art2MotorGear` and `Art4BodyBot` are exported inside out**, measuring
  −8435.0 and −113674.9 mm³.
- **`GripperActiveArm` and `GripperPassiveArm` each hold two solids**: the
  arm, and a loose Ø3.4 × 5.0 pin standing in its outer pivot hole. A
  builder slicing those files gets a plug printed inside the hole.
- **`GripperFinger` is used mirrored but published only one way**, so a
  builder printing from `step/` or `stl/` gets two identical jaws rather
  than the handed pair the assembly uses.
- **`Art1OptoFix`, `Art4BearingPlug` and `Art56Interface` are drawn and
  exported but placed in no assembly.**
- **The design models no fastener.** Every screw and nut in the model is
  derived from the parts' own Ø3.4 holes, Ø5.9 counterbores and 5.80
  across-flats pockets: 181 fasteners, 77 of them with nuts, and 85
  further hole stacks the geometry cannot classify.


## 📜 License

Thor is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/legalcode). You’re free to use, modify, and distribute this project under its terms.



## 🎥 Videos

[![Watch on YouTube](https://img.youtube.com/vi/F2CDeHrFr2k/0.jpg)](https://www.youtube.com/watch?v=F2CDeHrFr2k)

[![Watch on YouTube](https://img.youtube.com/vi/e0BGN1eIjiI/0.jpg)](https://www.youtube.com/watch?v=e0BGN1eIjiI)

[![Watch on YouTube](https://img.youtube.com/vi/nDCN46trJvs/0.jpg)](https://www.youtube.com/watch?v=nDCN46trJvs)
