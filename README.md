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
solid test --faceted simulation/thor.py   # the contracts, on meshes
solid test --exact simulation/thor.py     # the run a verdict is certified on
solid snapshot -o thor.png --autocenter --viewall
```

### What the sliders mean

| driver | what it measures | range |
| --- | --- | --- |
| `art1` | the base's yaw about Z | ±180° |
| `art2` | the shoulder's roll about Y, 202.0 mm up | ±90° |
| `art3` | the forearm's roll **in the machine frame** | ±135° |
| `art4` | the forearm's yaw about its own axis | ±180° |
| `art5` | the wrist's roll about Y, 556.0 mm up | ±105° |
| `art6` | the tool's roll about the wrist output axis | ±180° |
| `grip` | the clear opening between the two jaws | 0–69.94 mm |

`art3` is absolute, not relative to the upper arm, because the machine is:
the belt that sets the elbow runs from a pulley carried by the shoulder
housing rather than by the arm. Swing `art2` alone and the forearm keeps
pointing the same way while no elbow motor turns. The published joint
limits are not in this repository, so the ranges above are the mechanism's
own travel where the geometry bounds it and the full circle otherwise;
they are presentation only and clamp nothing.

The instructions are `Home`, `Ready`, `Reach`, `Pick`, `Place` and `Park`.

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
- **The elbow belt's two pulleys are not in the same plane.** The drive
  pulley's belt land is centred 7.85 mm away from the elbow pulley's along
  the shoulder axis, which no 6 mm belt can bridge.
- **The forearm belts are named for 208 mm and their pulleys need
  221.5 mm.** The design's own belt solid measures about 220, so it is the
  name that is wrong — but a builder buying by the name gets a belt that
  will not close.
- **All three belt solids are placed where their pulleys are not.** Both
  forearm belts lie flat in a plane perpendicular to their pulleys' axes.
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
  across-flats pockets: 216 fasteners, 111 of them with nuts, and 71
  further hole stacks the geometry cannot classify.


## 📜 License

Thor is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/legalcode). You’re free to use, modify, and distribute this project under its terms.



## 🎥 Videos

[![Watch on YouTube](https://img.youtube.com/vi/F2CDeHrFr2k/0.jpg)](https://www.youtube.com/watch?v=F2CDeHrFr2k)

[![Watch on YouTube](https://img.youtube.com/vi/e0BGN1eIjiI/0.jpg)](https://www.youtube.com/watch?v=e0BGN1eIjiI)

[![Watch on YouTube](https://img.youtube.com/vi/nDCN46trJvs/0.jpg)](https://www.youtube.com/watch?v=nDCN46trJvs)
