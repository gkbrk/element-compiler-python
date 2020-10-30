element-compiler-python
=======================

1. What is this project?

  This project is a compiler for single-file web components. It is meant to read
  Vue-like component files and output vanilla Javascript.

2. Using the compiler

  In the simplest form, the compiler can be executed as `./compile.py
  component.html`. This will read component.html and output JS code that
  implements this component.

2.1. Building multiple components

  The compiler can compiler multiple files at once. Just give them as arguments
  like `./compile.py comp1.html comp2.html`.

2.2. Stylesheets

  If the system has sassc (the SASS compiler) installed, the compiler can
  utilize it in order to minify the CSS. It can also allow the use of SASS
  syntax instead of vanilla CSS syntax. After the compilation, the component and
  its stylesheets will turn into vanilla JS and CSS.

3. License

  The project is licensed under the GNU General Public License. You can find a
  copy of the license in the LICENSE.txt file.

4. Contributing

  Contributions are welcome. They can be done by emailing a patch to
  opensource@gkbrk.com.

5. TODO list

5.1. Write documentation about Closure compiler

5.2. Provide more examples
