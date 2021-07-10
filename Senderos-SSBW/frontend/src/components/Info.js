import React from 'react';

class Info extends React.Component {
	render(){
		let id = this.props.e.id
		let file = this.props.e.fotos[0].file
		let pathname = "http://localhost/static/img/senderos"+"/"+id+"/"+file

		return (
			<div className="container" style={{marginTop: '5vw'}}>
				<button
					className="btn btn-primary"
					style={{marginTop: '2vw'}}
					onClick={() => this.props.handleInfo('')}
				>
					Volver
				</button>
				<h1>{this.props.e.nombre}</h1>
				<p className="mb-5">{ this.props.e.descripcion }</p>

				<img className="d-block mx-auto w-50" style={{height: '50%'}} src={pathname} alt="..."/>
				
			</div>
		)
	}
}

export default Info