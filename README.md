
```
demand-forecasting-project-modeling
├─ README.md
├─ backend
│  ├─ API
│  │  └─ weather_api.ipynb
│  ├─ features
│  │  ├─ __init__.py
│  │  ├─ time_features.ipynb
│  │  └─ time_features.py
│  ├─ main.py
│  ├─ models
│  │  ├─ __init__.py
│  │  ├─ check
│  │  │  ├─ baseline_model_code.ipynb
│  │  │  └─ demand_code.ipynb
│  │  ├─ linear_models.py
│  │  └─ tree_models.py
│  └─ train
│     └─ train-linear.py
├─ data
├─ documents
│  └─ command.txt
├─ frontend
│  ├─ .env
│  ├─ .prettierrc
│  ├─ .yarnrc.yml
│  ├─ CODE_OF_CONDUCT.md
│  ├─ LICENSE
│  ├─ README.md
│  ├─ eslint.config.mjs
│  ├─ favicon.svg
│  ├─ index.html
│  ├─ jsconfig.json
│  ├─ jsconfig.node.json
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ src
│  │  ├─ App.jsx
│  │  ├─ api
│  │  │  └─ menu.js
│  │  ├─ assets
│  │  │  ├─ images
│  │  │  │  └─ users
│  │  │  │     ├─ avatar-1.png
│  │  │  │     ├─ avatar-2.png
│  │  │  │     ├─ avatar-3.png
│  │  │  │     ├─ avatar-4.png
│  │  │  │     ├─ avatar-5.png
│  │  │  │     └─ avatar-group.png
│  │  │  ├─ style.css
│  │  │  └─ third-party
│  │  │     ├─ apex-chart.css
│  │  │     └─ react-table.css
│  │  ├─ components
│  │  │  ├─ @extended
│  │  │  │  ├─ AnimateButton.jsx
│  │  │  │  ├─ Avatar.jsx
│  │  │  │  ├─ Breadcrumbs.jsx
│  │  │  │  ├─ Dot.jsx
│  │  │  │  ├─ IconButton.jsx
│  │  │  │  └─ Transitions.jsx
│  │  │  ├─ Loadable.jsx
│  │  │  ├─ Loader.jsx
│  │  │  ├─ MainCard.jsx
│  │  │  ├─ ScrollTop.jsx
│  │  │  ├─ cards
│  │  │  │  ├─ AuthFooter.jsx
│  │  │  │  └─ statistics
│  │  │  │     └─ AnalyticEcommerce.jsx
│  │  │  ├─ logo
│  │  │  │  ├─ LogoIcon.jsx
│  │  │  │  ├─ LogoMain.jsx
│  │  │  │  └─ index.jsx
│  │  │  └─ third-party
│  │  │     └─ SimpleBar.jsx
│  │  ├─ config.js
│  │  ├─ contexts
│  │  │  ├─ ConfigContext.jsx
│  │  │  └─ README.md
│  │  ├─ data
│  │  │  └─ README.md
│  │  ├─ hooks
│  │  │  ├─ README.md
│  │  │  ├─ useConfig.js
│  │  │  └─ useLocalStorage.js
│  │  ├─ index.jsx
│  │  ├─ layout
│  │  │  ├─ Auth
│  │  │  │  └─ index.jsx
│  │  │  └─ Dashboard
│  │  │     ├─ Drawer
│  │  │     │  ├─ DrawerContent
│  │  │     │  │  ├─ NavCard.jsx
│  │  │     │  │  ├─ Navigation
│  │  │     │  │  │  ├─ NavGroup.jsx
│  │  │     │  │  │  ├─ NavItem.jsx
│  │  │     │  │  │  └─ index.jsx
│  │  │     │  │  └─ index.jsx
│  │  │     │  ├─ DrawerHeader
│  │  │     │  │  ├─ DrawerHeaderStyled.js
│  │  │     │  │  └─ index.jsx
│  │  │     │  ├─ MiniDrawerStyled.js
│  │  │     │  └─ index.jsx
│  │  │     ├─ Footer.jsx
│  │  │     ├─ Header
│  │  │     │  ├─ AppBarStyled.jsx
│  │  │     │  ├─ HeaderContent
│  │  │     │  │  ├─ MobileSection.jsx
│  │  │     │  │  ├─ Notification.jsx
│  │  │     │  │  ├─ Profile
│  │  │     │  │  │  ├─ ProfileTab.jsx
│  │  │     │  │  │  ├─ SettingTab.jsx
│  │  │     │  │  │  └─ index.jsx
│  │  │     │  │  ├─ Search.jsx
│  │  │     │  │  └─ index.jsx
│  │  │     │  └─ index.jsx
│  │  │     └─ index.jsx
│  │  ├─ menu-items
│  │  │  ├─ dashboard.jsx
│  │  │  ├─ index.jsx
│  │  │  ├─ page.jsx
│  │  │  ├─ support.jsx
│  │  │  └─ utilities.jsx
│  │  ├─ pages
│  │  │  ├─ auth
│  │  │  │  ├─ Login.jsx
│  │  │  │  └─ Register.jsx
│  │  │  ├─ component-overview
│  │  │  │  ├─ color.jsx
│  │  │  │  ├─ shadows.jsx
│  │  │  │  └─ typography.jsx
│  │  │  ├─ dashboard
│  │  │  │  └─ default.jsx
│  │  │  └─ extra-pages
│  │  │     └─ sample-page.jsx
│  │  ├─ reportWebVitals.js
│  │  ├─ routes
│  │  │  ├─ LoginRoutes.jsx
│  │  │  ├─ MainRoutes.jsx
│  │  │  └─ index.jsx
│  │  ├─ sections
│  │  │  ├─ auth
│  │  │  │  ├─ AuthBackground.jsx
│  │  │  │  ├─ AuthCard.jsx
│  │  │  │  ├─ AuthLogin.jsx
│  │  │  │  ├─ AuthRegister.jsx
│  │  │  │  └─ AuthWrapper.jsx
│  │  │  └─ dashboard
│  │  │     ├─ SalesChart.jsx
│  │  │     └─ default
│  │  │        ├─ IncomeAreaChart.jsx
│  │  │        ├─ MonthlyBarChart.jsx
│  │  │        ├─ OrdersTable.jsx
│  │  │        ├─ ReportAreaChart.jsx
│  │  │        ├─ SaleReportCard.jsx
│  │  │        └─ UniqueVisitorCard.jsx
│  │  ├─ themes
│  │  │  ├─ custom-shadows.jsx
│  │  │  ├─ index.jsx
│  │  │  ├─ overrides
│  │  │  │  ├─ Badge.js
│  │  │  │  ├─ Button.js
│  │  │  │  ├─ ButtonBase.js
│  │  │  │  ├─ CardContent.js
│  │  │  │  ├─ Checkbox.jsx
│  │  │  │  ├─ Chip.js
│  │  │  │  ├─ Drawer.js
│  │  │  │  ├─ FormHelperText.js
│  │  │  │  ├─ IconButton.js
│  │  │  │  ├─ InputLabel.js
│  │  │  │  ├─ LinearProgress.js
│  │  │  │  ├─ Link.js
│  │  │  │  ├─ ListItemButton.jsx
│  │  │  │  ├─ ListItemIcon.jsx
│  │  │  │  ├─ OutlinedInput.js
│  │  │  │  ├─ Tab.js
│  │  │  │  ├─ TableBody.js
│  │  │  │  ├─ TableCell.js
│  │  │  │  ├─ TableHead.js
│  │  │  │  ├─ TableRow.js
│  │  │  │  ├─ Tabs.js
│  │  │  │  ├─ Tooltip.js
│  │  │  │  ├─ Typography.js
│  │  │  │  └─ index.js
│  │  │  ├─ palette.js
│  │  │  ├─ theme
│  │  │  │  └─ index.js
│  │  │  └─ typography.js
│  │  ├─ utils
│  │  │  ├─ colorUtils.js
│  │  │  ├─ getColors.js
│  │  │  ├─ getShadow.js
│  │  │  ├─ password-strength.js
│  │  │  └─ password-validation.js
│  │  └─ vite-env.d.js
│  ├─ vite.config.mjs
│  └─ yarn.lock
├─ function
│  └─ eda
│     ├─ eda_blinkit_master_data.ipynb
│     └─ eda_weather.ipynb
├─ old_README.md
└─ requirements.txt

```